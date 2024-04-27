from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import sys
import json

#import time
#import requests

creds_file_name = "credentials"

def parse_email(email):
    # NOTE: Converting string to utf-8
    # https://stackoverflow.com/questions/72563734/decode-a-utf8-string-in-python
    email = (email
            .encode()
            .decode('unicode_escape')
            .encode('latin1').decode())
    search_url = f"https://www.ua.pt/pt/pesquisa/p/?q={email}"
    #print(f"Email:{email}")

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get(search_url)

    personal_url = "n/a"

    try:
        wait = WebDriverWait(driver, 5) # maximum page load timeout

        # NOTE: personal user information containers appear withing a <div class="sc-kgoBCf cQxJJ">
        #       it seems we only need to wait until the class "cQxJJ" is present in the page though
        #wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sc-kgoBCf')))
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.CLASS_NAME, 'cQxJJ')),
                EC.presence_of_element_located((By.XPATH, '//*[contains(text(),"Sem conteúdos para a pesquisa")]'))
            )
        )
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # find all <a> elements with href containing "/pt/p/"
        personal_pages = soup.find_all('a', href=lambda href: href and "/pt/p/" in href)
        associated_email = soup.find_all('p', class_='sc-gqjmRU gndnXb')    # ensure that the personal page really corresponds to the email we are searching for (needed in the case of "cribeiro@ua.pt", for example)

        # print the href attribute of matching links
        for i in range (len(personal_pages)):
            # ensure that we only read the email we captured
            if (associated_email[i].get_text(strip=True).split(" | ")[-1] != email):
                continue

            #print(f"Link:https://www.ua.pt{personal_pages[i]['href']}")
            personal_url = f"https://www.ua.pt{personal_pages[i]['href']}"

            """
            driver.get(personal_url)
            
            # NOTE: this time, for specific users, we want to wait for <div class="sc-kgoBCf iOknku">
            #       so the class "iOknku" needs to be present in the page
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'iOknku')))
            soup = BeautifulSoup(driver.page_source, 'lxml')

            infos = soup.find_all('div', class_='sc-kgoBCf iOknku')
            for info in infos:
                
                name = info.find_all('h1', class_='sc-gqjmRU gvTmvY')
                if len(name) > 0:
                    print(f"Nome:{name[0].get_text(strip=True)}\n")

                local = info.find_all('h3', class_='sc-jzJRlG leiSEw')
                if len(local) > 0:
                    print(f"Local:{local[0].get_text(strip=True)}")

                personal_items = info.find_all('div', class_='sc-hrWEMg gbvwiX')
                for item in personal_items:
                    print(f"\t{item.get_text(strip=True)}")

                functional_duties = info.find_all('div', class_='sc-hrWEMg fjHrLB')
                for duty in functional_duties:
                    print(f"\t{duty.get_text(strip=True)}")
            """

            """
            functions = soup.find_all('h3', class_='sc-jzJRlG leiSEw')
            for function in functions:
                print(f"Funcao:{function.get_text(strip=True)}")

            personal_items = soup.find_all('div', class_='sc-hrWEMg gbvwiX')
            for item in personal_items:
                print(item.get_text(strip=True))

            personal_items = soup.find_all('div', class_='sc-hrWEMg fjHrLB')
            for item in personal_items:
                print(item.get_text(strip=True))
            """

    except:
        #print(f"(ERROR) Email Parser: No personal page found for email '{email}'")
        #print("Categoria:Outro")
        pass

    # close webdriver
    driver.quit()

    return personal_url

def parse_arguments():
    global creds_file_name

    print("Email Parser: Parsing arguments...\n")

    cur_arg = ''
    for a in sys.argv:
        # reading argument
        if len(a) > 2 and a[0:2] == '--':
            #print(f"Reading argument '{a[2:]}'")
            cur_arg = a[2:]
        # reading attribute
        elif cur_arg != '' and a[0:2] != '--':
            #print(f"Reading attribute '{a}' for argument '{cur_arg}'")

            if cur_arg == 'creds':
                creds_file_name += f"-{a}"
                print(f"\tcreds = {a}")

            cur_arg = ''

    print()

if __name__ == '__main__':
    parse_arguments()

    creds_file_name += ".json"

    vulnerable_count = 0
    user_count = 0

    try:
        with open(creds_file_name, "r+") as credentials_file:
            try:
                json_credentials = json.load(credentials_file)

                for email in json_credentials.keys():
                    user_count += 1
                    # print extra information in case the user is vulnerable
                    if (len(json_credentials[email]) > 0):
                        parse_email(email)
                        vulnerable_count += 1
                        print("===================================")
                
            # JSONDecodeError error, file can either be empty or not in json format
            except ValueError:
                print(f"(ERROR) Email Parser: Could not load json object from '{creds_file_name}'")
    except FileNotFoundError:
        print(f"(ERROR) Email Parser: Credentials file '{creds_file_name}' not found")

    if (user_count > 0):
        print(f"User emails: {user_count} ; Vulnerable users: {vulnerable_count} -> {(vulnerable_count / user_count * 100) :.2f} %")

    #parse_email('joanarcorreia@ua.pt')