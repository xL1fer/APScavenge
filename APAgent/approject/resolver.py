# NOTE: Running the resolver locally:
#       flask --app [path_to_resolver/]resolver run
#
#       Optional flags:
#
#           --host=0.0.0.0      # open server to the network
#           --debug             # run in debug mode (reload on code change and interactive browser debugger)
#
#   https://flask.palletsprojects.com/en/3.0.x/quickstart/
#
# NOTE: For now keep running through the flask command, the python one keeps getting the network manager down
#
#   sudo flask --app resolver run --debug --host=0.0.0.0
#   (sudo python resolver.py --iface eth0 --centralip 127.0.0.1:80)

from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from markupsafe import escape       # escape to prevent injection atacks
from flask import url_for           # build a URL to a specific function
from flask import abort             # abort request early with an error code
from flask import redirect          # redirect user to another endpoint
from flask import request           # POST/GET methods
from flask import render_template   # template engine

import os
import sys
import requests
import json
import subprocess
import signal
from pathlib import Path
from multiprocessing import Queue
from multiprocessing import Process
import atexit
import psutil

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import load_pem_x509_certificate

import netifaces

import dotenv

from pymana import pymana

# Load public key (certificate)
with open("keys/apscavenge.pem", 'rb') as cert_file:
    cert_data = cert_file.read()
    cert = load_pem_x509_certificate(cert_data, default_backend())
    public_key = cert.public_key()

# Load private key
with open("keys/apscavenge.key", 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,  # Password in case the private key file is encrypted
        backend=default_backend()
    )

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__,
            static_url_path='', 
            static_folder='apagent/static',         #BASE_DIR / 'approject' / 'apagent' / 'static',
            template_folder='apagent/templates')    #BASE_DIR / 'approject' / 'apagent' / 'templates')

g_iface = 'eth0'
g_central_ip = '127.0.0.1:80' # NOTE: placeholder ip, is replaced later on
g_agent_id = '-1'
g_agent_ip = '127.0.0.1:80'   # NOTE: placeholder ip, is replaced later on
g_agent_area = 'none'
g_is_attacking = False
g_attack_process = None
g_queue = Queue()

#with app.test_request_context():
#    url_for('static', filename='css/style.css')

#####################################
# Helper functions                  #
#####################################

def exec_cmd(cmd):
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
        
        # wait process to complete and capture output
        output, error = process.communicate()
        if output:
            print(output)

        # print any error
        if error:
            print(error)
    except Exception as e:
        print(f"(ERROR) APAgent: Could not execute command")

def stop_process(process_name):
    #if process is not None and process.is_alive():
    #    process.terminate()
    #    process.join()

    #exec_cmd("kill -15 $(pidof hostapd)")

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.kill()
            print(f"(INFO) APAgent: Process '{process_name}' killed")
            return
        
    print(f"(INFO) APAgent: Process '{process_name}' not running")

def before_exit():
    global g_is_attacking, g_attack_process

    # stop attacking
    if g_is_attacking:
        stop_process('hostapd')
        g_is_attacking = False

# hook program exit
atexit.register(before_exit)

def is_int(arg):
    return type(arg) == int or type(arg) == str and arg.isdigit()

def public_key_encryption(data_dict):
    global public_key
    plaintext = json.dumps(data_dict).encode('utf-8')

    # encrypt payload with public key
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {'encrypted_data': ciphertext.decode('latin-1')}

def private_key_decryption(data):
    global private_key
    plain_data = {}
    if 'encrypted_data' in data:

        # decrypt ciphertext with private key
        plaintext = private_key.decrypt(
            data['encrypted_data'].encode('latin-1'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        try:
            return json.loads(plaintext)
        except ValueError as e:
            print("(ERROR) APAgent: Decrypted text is not a valid json format")
    
    return plain_data

#####################################
# Periodic functions                #
#####################################

def heartbeat_central():
    #print('Sending heartbeat to central server...')

    global g_central_ip, g_agent_id, g_agent_ip, g_agent_area, g_is_attacking, g_attack_process

    try:
        url = f'http://{g_central_ip}/central-heartbeat-api'
        data = {'id': g_agent_id, 'ip': g_agent_ip, 'area': g_agent_area, 'alias_name': g_agent_area, 'is_attacking': g_is_attacking}

        #print(f"Heartbeat request: {str(data)}")
        #response = requests.post(url, json=data, timeout=5)
        response = requests.post(url, json=public_key_encryption(data), timeout=5)

        #print(f'Heartbeat response: status code {response.status_code} | content {response.content}')

        try:
            response_content = json.loads(response.content.decode("UTF-8"))
            plain_data = private_key_decryption(response_content)

            if 'id' in plain_data and is_int(plain_data['id']):
                g_agent_id = plain_data['id']
                #print(f"New agent_id: {g_agent_id}")
            elif 'last_heartbeat' not in plain_data:
                print('(ERROR) APAgent: Bad heartbeat response')
        except ValueError as e:
            #print(e)
            print("(ERROR) APAgent: Response is not a valid json format")

    except requests.exceptions.RequestException as e:
        #print(e)
        print('(ERROR) APAgent: Could not execute heartbeat central request')

        # stop attacking
        if g_is_attacking:
            stop_process('hostapd')
            g_is_attacking = False

#####################################
# API Endpoints                     #
#####################################

@app.get('/agent-heartbeat-api')
def agent_heartbeat():
    global g_agent_id, g_is_attacking
    return jsonify(public_key_encryption({'message': 'Heartbeat received.', 'agent_id': g_agent_id, 'is_attacking': g_is_attacking})), 200

@app.post('/start-attack-api')
def start_attack():
    global g_central_ip, g_agent_id, g_agent_area, g_is_attacking, g_attack_process, g_queue

    content = request.get_json()
    plain_data = private_key_decryption(content)
    if 'id' not in plain_data or not is_int(plain_data['id']) or int(plain_data['id']) != int(g_agent_id):
        return jsonify(public_key_encryption({'message': 'Wrong agent id.'})), 400

    if g_is_attacking:
        return jsonify(public_key_encryption({'message': 'Already attacking.'})), 400
    
    #attack_process = subprocess.Popen(['python', 'pymana.py'] + ['--iface', 'wlan0', '--creds', agent_area, '--area', agent_area, '--centralip', central_ip, '--queueid', str(id(queue))], cwd=BASE_DIR / "pymana")

    # clear queue
    while not g_queue.empty():
        g_queue.get()

    g_attack_process = Process(target=pymana.main, args=("wlan0", g_agent_area, "eduroam", g_agent_area, g_central_ip, g_queue,))
    g_attack_process.start()

    message = g_queue.get()
    if message != 'Pymana started':
        return jsonify(public_key_encryption({'message': 'Failed to start the attack.'})), 400

    g_is_attacking = True

    return jsonify(public_key_encryption({'message': 'Attack started.'})), 200

@app.post('/stop-attack-api')
def stop_attack():
    global g_agent_id, g_is_attacking, g_attack_process

    content = request.get_json()
    plain_data = private_key_decryption(content)
    if 'id' not in plain_data or not is_int(plain_data['id']) or int(plain_data['id']) != int(g_agent_id):
        return jsonify(public_key_encryption({'message': 'Wrong agent id.'})), 400

    if not g_is_attacking:
        return jsonify(public_key_encryption({'message': 'Currently not attacking.'})), 400
    
    #attack_process.send_signal(signal.SIGINT)
    #attack_process.wait()
    stop_process('hostapd')
    g_is_attacking = False

    return jsonify(public_key_encryption({'message': 'Attack stopped.'})), 200


@app.post('/clear-deny-list-api')
def clear_deny_list():
    global g_agent_id, g_is_attacking

    content = request.get_json()
    plain_data = private_key_decryption(content)
    if 'id' not in plain_data or not is_int(plain_data['id']) or int(plain_data['id']) != int(g_agent_id):
        return jsonify(public_key_encryption({'message': 'Wrong agent id.'})), 400
    
    # clear deny list
    with open(f"pymana/hostapd.deny", 'w'):
        pass

    if g_is_attacking:
        # reload hostapd configs
        exec_cmd("kill -1 $(pidof hostapd)")

    return jsonify(public_key_encryption({'message': 'Deny list cleared.'})), 200

#####################################
# Main                              #
#####################################

def main():
    global g_iface, g_central_ip, g_agent_ip, g_agent_area

    # prevent schedule functions from executing twice (one by the master and another child process)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        
        # get communication interface and central ip from env file
        dotenv_file = BASE_DIR / '.env.local'
        if os.path.isfile(dotenv_file):
            dotenv.load_dotenv(dotenv_file)
        g_iface = os.getenv('COM_IFACE', 'eth0')
        g_central_ip = os.getenv('CENTRAL_IP', '127.0.0.1:80')
        g_agent_area = os.getenv('AGENT_AREA', 'none')

        try:
            g_agent_ip = f"{netifaces.ifaddresses(g_iface)[netifaces.AF_INET][0]['addr']}:80"
        except:
            print(f'(ERROR) APAgent: Could not get address from interface "{g_iface}"')

        heartbeat_central() # Perform the first heartbeat

        scheduler = BackgroundScheduler()
        job = scheduler.add_job(heartbeat_central, 'interval', seconds=10)
        scheduler.start()

main()





# runnig with "python resolver.py"
#if __name__ == "__main__":
#    main()
#    app.run(host='0.0.0.0') #app.run(debug=True, host='0.0.0.0')
# runnig with "flask --app resolver run"
#else:
#    main()