from django.shortcuts import render, redirect
from django.views.generic import View   # django generic View class
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator # database objects paginator
from django.contrib.auth import authenticate, login, logout # import Django built in functions

from .models import Seizure, InfoHistory, PasswordHash, AgentStatus#, User
from .forms import LoginForm, PageItemsSelectForm, SelectTableForm, SearchTableForm
from .serializers import SeizureSerializer, InfoHistorySerializer, PasswordHashSerializer, AgentStatusSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.template.defaulttags import register

from django.utils import timezone

import requests
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import load_pem_x509_certificate

# Create your views here.

#from .tasks import init_tasks

#init_tasks()

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

#####################################
# Custom Django Template Filters    #
#####################################

@register.filter
def get_value(dictionary, key):
    return getattr(dictionary, key)

@register.filter
def mult(value1, value2):
    return value1 * value2

#####################################
# Helper Functions                  #
#####################################

def authentication_handler(request, auth_required=True):
    if auth_required:
        if not request.user.is_authenticated:
            request.session['auth_message'] = 'The specified page requires authentication.'
            return False

    request.session['auth_message'] = ""

    return True

def get_model_class(request, select_table_form, model_string):

    default_model_class = select_table_form.fields['table_select'].initial
    if select_table_form.is_valid():
        default_model_class = select_table_form.cleaned_data['table_select']

    default_model_class = globals().get(default_model_class, None)

    if request.POST.get(model_string) == 'seizure':
        return Seizure
    elif request.POST.get(model_string) == 'infohistory':
        return InfoHistory
    elif request.POST.get(model_string) == 'passwordhash':
        return PasswordHash

    return default_model_class  # NOTE: giving Seizure model class by default

def table_data_handler(request, model_class, select_table_form, search_table_form, page_items_select_form):
    """
    cur_page = request.GET.get('page', 1)
    try:
        cur_page = int(cur_page)
    except:
        cur_page = 1
    """

    # TODO: reset cur_page when items_per_page change?

    table_data = {}
    table_data["fields"] = [f.name for f in model_class._meta.get_fields() if not f.is_relation and not f.one_to_one]
    table_data["relation_fields"] = [f.name for f in model_class._meta.get_fields() if f.is_relation]
    table_data["current_model"] = model_class.__name__.lower()

    if not request.POST.get("ajaxSubTableUpdate"):
        objects = None

        cur_page = int(page_items_select_form.fields['cur_page'].initial)
        items_per_page = int(page_items_select_form.fields['page_items'].initial)

        if page_items_select_form.is_valid():
            cur_page = int(page_items_select_form.cleaned_data['cur_page'])
            items_per_page = int(page_items_select_form.cleaned_data['page_items'])

        # NOTE: Since the search_table_form.filter_field select has no default values, as they are only set directly in the dashboard_table.html template,
        #       we need to set them here, otherwise the form is considered invalid for cona values that do not correspond to any default
        filter_field = request.POST.get('filter_field')
        if filter_field in table_data["fields"]:    # Ensure that the filter_field is not forged
            search_table_form.fields['filter_field'].choices = [(filter_field, filter_field)]
        
        if search_table_form.is_valid():
            filter_params = {f"{search_table_form.cleaned_data['filter_field']}__contains": search_table_form.cleaned_data['search_field']}
            objects = model_class.objects.filter(**filter_params)
        else:
            objects = model_class.objects.all()

        paginator = Paginator(objects, items_per_page)

        if cur_page < paginator.page_range.start:
            cur_page = paginator.page_range.start
        elif cur_page >= paginator.page_range.stop:
            cur_page = paginator.page_range.stop - 1

        table_data["items_start"] = (cur_page - 1) * items_per_page + 1
        table_data["items_stop"] = cur_page * items_per_page if cur_page * items_per_page < paginator.count else paginator.count
        table_data["items_count"] = paginator.count
        table_data["items_data"] = paginator.page(cur_page).object_list
        table_data["max_page"] = paginator.page_range.stop - 1

    else:
        prev_model_class = get_model_class(request, select_table_form, 'previousModel')

        #print(f">>> {prev_model_class} -> {prev_model_class._meta.pk.name}")
        #print(f">>> {model_class} -> {model_class._meta.pk.name}")

        #foreign_keys = [field.name for field in model_class._meta.fields if field.is_relation and field.many_to_one]
        #print(f"{table_data["relation_fields"][-1]}__{prev_model_class._meta.pk.name}: {request.POST.get('requestValue')}")

        filter_params = {f"{table_data["relation_fields"][-1]}__{prev_model_class._meta.pk.name}": request.POST.get('requestValue')}
        objects = model_class.objects.filter(**filter_params)
        #objects = model_class.objects.filter(seizure_email__email=request.POST.get('requestValue'))
        #objects = model_class.objects.filter(info_history__id=request.POST.get('requestValue'))

        table_data["items_data"] = objects

    return table_data

def update_active_agents():
    agentstatus_objects = AgentStatus.objects.all()
    for agentstatus in agentstatus_objects:
        time_difference = timezone.now() - agentstatus.last_heartbeat

        if time_difference.total_seconds() > 25:
            agentstatus.delete()

def is_int(arg):
    return type(arg) == int or type(arg) == str and arg.isdigit()

def public_key_encryption(data_dict):
    plaintext = json.dumps(data_dict).encode('utf-8')

    # Encrypt payload with public key
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
    plain_data = {}
    if 'encrypted_data' in data:

        # Decrypt ciphertext with private key
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
            print("(ERROR) APScavenge: Decrypted text is not a valid json format")
    
    return plain_data

#####################################
# View Classes                      #
#####################################

class LoginView(View):
    """Login page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        
        return render(request, 'login.html', {'login_form': LoginForm()})

    def post(self, request):
        assert isinstance(request, HttpRequest)
        authentication_handler(request, False)
        
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # get "username" and "password" using the cleaned_data method after form validation
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                return redirect('index')

        return render(request, 'login.html', {'login_form': login_form, 'login_message': 'Invalid user credentials.'})

class DashboardView(View):
    """Dashboard page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        select_table_form = SelectTableForm()
        search_table_form = SearchTableForm()
        page_items_select_form = PageItemsSelectForm()

        model_class = get_model_class(request, select_table_form, 'requestModel')
        table_data = table_data_handler(request, model_class, select_table_form, search_table_form, page_items_select_form)
        
        return render(request, 'dashboard.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})

    def post(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        select_table_form = SelectTableForm(request.POST)
        search_table_form = SearchTableForm(request.POST)
        page_items_select_form = PageItemsSelectForm(request.POST) if PageItemsSelectForm(request.POST).is_valid() else PageItemsSelectForm()

        model_class = get_model_class(request, select_table_form, 'requestModel')
        table_data = table_data_handler(request, model_class, select_table_form, search_table_form, page_items_select_form)

        # ajax request, return only a sub portion of the dashboard content
        if request.POST.get('ajaxTableUpdate'):
            if request.POST.get('ajaxSubTableUpdate'):
                return render(request, 'dashboard_subtable.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})
            
            return render(request, 'dashboard_table.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})
        
        return render(request, 'dashboard.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})
    
class InfrastructureView(View):
    """Infrastructure page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        update_active_agents()
        agentstatus_objects = AgentStatus.objects.all()
        
        return render(request, 'infrastructure.html', {"agentstatus_objects": agentstatus_objects})

    def post(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        update_active_agents()
        agentstatus_objects = AgentStatus.objects.all()

        if request.POST.get('agentAction'):
            agentAction = request.POST['agentAction'].split('-')
            if is_int(agentAction[0]) and AgentStatus.objects.filter(id=agentAction[0]).exists():
                agentstatus = AgentStatus.objects.get(id=agentAction[0])
                # Ensure we are not already performing a request to this agent
                if not agentstatus.is_requesting:
                    agentstatus.is_requesting = True
                    agentstatus.save()
                    
                    if agentAction[1] == 'start':
                        try:
                            url = f'http://{agentstatus.ip}/start-attack-api'
                            response = requests.post(url, json=public_key_encryption({"id": int(agentAction[0])}))
                            #print(f'Response: status code {response.status_code} | content {response.content}')

                            if response.status_code == 200:
                                agentstatus.is_attacking = True
                            agentstatus.save()

                            for agent in agentstatus_objects:
                                if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                                    try:
                                        agent.message = private_key_decryption(json.loads(response.content.decode("UTF-8")))['message']
                                        if agent.message == "Wrong agent id.":
                                            agentstatus.delete()
                                    except ValueError as e:
                                        pass

                        except requests.exceptions.RequestException as e:
                            agentstatus.delete()

                    elif agentAction[1] == 'stop':
                        try:
                            url = f'http://{agentstatus.ip}/stop-attack-api'
                            response = requests.post(url, json=public_key_encryption({"id": int(agentAction[0])}))
                            #print(f'Response: status code {response.status_code} | content {response.content}')

                            agentstatus.is_attacking = False
                            agentstatus.save()

                            for agent in agentstatus_objects:
                                if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                                    try:
                                        agent.message = private_key_decryption(json.loads(response.content.decode("UTF-8")))['message']
                                        if agent.message == "Wrong agent id.":
                                            agentstatus.delete()
                                    except ValueError as e:
                                        pass

                        except requests.exceptions.RequestException as e:
                            agentstatus.delete()
                    
                    if AgentStatus.objects.filter(id=agentAction[0]).exists():
                        agentstatus.is_requesting = False
                        agentstatus.save()
                else:
                    pass
                
        if request.POST.get('ajaxGridUpdate'):
            return render(request, 'infrastructure_grid.html', {"agentstatus_objects": agentstatus_objects})

        return render(request, 'infrastructure.html', {"agentstatus_objects": agentstatus_objects})

class InfrastructureAgentView(View):
    """Infrastructure agent page render handler"""

    def get(self, request, area):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        update_active_agents()
        
        if AgentStatus.objects.filter(area=area).exists():
            agentstatus = AgentStatus.objects.get(area=area)

            infohistory_objects = InfoHistory.objects.filter(area=area, capture_time__gte=timezone.now() - timezone.timedelta(minutes=15))

            agent_seizures = {}
            for infohistory in infohistory_objects:
                password_hash = None
                try:
                    password_hash = infohistory.passwordhash
                except PasswordHash.DoesNotExist:
                    pass

                time_past = (timezone.now() - infohistory.capture_time).total_seconds() / 60
                agent_seizures.setdefault(infohistory.seizure_email.email, []).append([f"Capture {infohistory.id}", f"{time_past:.2f} minute(s) ago", "Vulnerable" if password_hash else "Secure"])

            return render(request, 'infrastructure_agent.html', {'agentstatus': agentstatus, 'agent_seizures': agent_seizures})
        
        return redirect('infrastructure')

    def post(self, request, area):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        update_active_agents()
        
        if AgentStatus.objects.filter(area=area).exists():
            agentstatus = AgentStatus.objects.get(area=area)

            if request.POST.get("ajaxAliasNameUpdate"):
                if len(request.POST['ajaxAliasNameUpdate']) < 65:
                    agentstatus.alias_name = request.POST['ajaxAliasNameUpdate']
                    agentstatus.save()
                return HttpResponse(status=200)
            elif request.POST.get("ajaxAgentOption"):
                if request.POST['ajaxAgentOption'] == 'clear-deny-list':
                    try:
                        url = f'http://{agentstatus.ip}/clear-deny-list-api'
                        response = requests.post(url, json=public_key_encryption({"id": int(agentstatus.id)}))
                        #print(f'Response: status code {response.status_code} | content {response.content}')

                        if private_key_decryption(json.loads(response.content.decode("UTF-8")))['message'] == "Wrong agent id.":
                            agentstatus.delete()
                            return HttpResponse(status=400)

                    except requests.exceptions.RequestException as e:
                        agentstatus.delete()
                        return HttpResponse(status=400)
                return HttpResponse(status=200)

            infohistory_objects = InfoHistory.objects.filter(area=area, capture_time__gte=timezone.now() - timezone.timedelta(minutes=15))

            agent_seizures = {}
            for infohistory in infohistory_objects:
                password_hash = None
                try:
                    password_hash = infohistory.passwordhash
                except PasswordHash.DoesNotExist:
                    pass

                time_past = (timezone.now() - infohistory.capture_time).total_seconds() / 60
                agent_seizures.setdefault(infohistory.seizure_email.email, []).append([f"Capture {infohistory.id}", f"{time_past:.2f} minute(s) ago", "Vulnerable" if password_hash else "Secure"])

            return render(request, 'infrastructure_agent.html', {'agentstatus': agentstatus, 'agent_seizures': agent_seizures})
        
        return redirect('infrastructure')

#####################################
# View Functions                    #
#####################################

def index_view(request):
    """Index page render handler"""
    assert isinstance(request, HttpRequest)
    authentication_handler(request, False)
    
    return render(request, 'index.html')

def logout_view(request):
    """Logout request handler"""
    assert isinstance(request, HttpRequest)
    authentication_handler(request, False)

    logout(request)
    return redirect('index')

########################

def insert_dummy_data(request):
    """Fill database with dummy data"""
    assert isinstance(request, HttpRequest)
    if not authentication_handler(request):
        return HttpResponse('<h3>You must be authenticated.<h3>')
    
    dummy_count = 10

    for i in range(dummy_count):
        Seizure(email=f"dummy{i}@realm").save()

    for i in range(dummy_count):
        info_history = InfoHistory(user_type=f"Dummy Type {i}", user_info_id=-1, area=f"local", seizure_email_id=f"dummy{i}@realm")
        info_history.save()

        if i % 2:
            #print(f"Inserting password hash for info history object {info_history}")
            PasswordHash(asleap=f"asleap_dummy_hash_{info_history.id}", jtr=f"jtr_dummy_hash_{info_history.id}", hashcat=f"hashcat_dummy_hash_{info_history.id}", info_history_id=info_history.id).save()

    return HttpResponse('<h3>Dummy data inserted.<h3>')

def delete_dummy_data(request):
    """Delete dummy data from database"""
    assert isinstance(request, HttpRequest)
    if not authentication_handler(request):
        return HttpResponse('<h3>You must be authenticated.<h3>')
    
    Seizure.objects.all().delete()

    return HttpResponse('<h3>Dummy data deleted.<h3>')

#####################################
# API Endpoints                     #
#####################################

class CustomAuthToken(ObtainAuthToken):
    """API custom token authentication"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        }, status=status.HTTP_200_OK)
    
class CentralHeartbeatAPI(APIView):
    """Central heartbeat handler"""

    # add permission to check if user is authenticated
    #permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        update_active_agents()

        plain_data = private_key_decryption(request.data)

        # Verify if request is from an already existing area agent
        if 'area' in plain_data and AgentStatus.objects.filter(area=plain_data['area']).exists():
            if 'id' in plain_data and is_int(plain_data['id']) and AgentStatus.objects.filter(id=plain_data['id']).exists():
                agentstatus = AgentStatus.objects.get(id=plain_data['id'])
                agentstatus.last_heartbeat = timezone.now()
                if 'is_attacking' in plain_data:
                    agentstatus.is_attacking = True if plain_data['is_attacking'] == True else False
                agentstatus.save()

                return Response(public_key_encryption({"last_heartbeat": str(agentstatus.last_heartbeat)}), status=status.HTTP_200_OK)
            else:
                return Response(public_key_encryption({"message": "Wrong area agent id."}), status=status.HTTP_400_BAD_REQUEST)

        serializer = AgentStatusSerializer(data=plain_data)
        if serializer.is_valid():
            serializer.save()
            return Response(public_key_encryption(serializer.data), status=status.HTTP_201_CREATED)

        return Response(public_key_encryption(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

class SeizureAPI(APIView):
    """Seizure API handler"""

    # add permission to check if user is authenticated
    #permission_classes = [permissions.IsAuthenticated]

    """
    def get(self, request, *args, **kwargs):
        seizure = Seizure.objects.all()
        serializer = SeizureSerializer(seizure, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    """

    def post(self, request, *args, **kwargs):
        if 'email' in request.data and AgentStatus.objects.filter(area=request.data['email']).exists():
            #seizure = Seizure.objects.get(email=request.data['email'])
            return Response(public_key_encryption({'message': 'Email already registered.'}), status=status.HTTP_200_OK)

        serializer = SeizureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(public_key_encryption(serializer.data), status=status.HTTP_201_CREATED)
        
        return Response(public_key_encryption(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

class InfoHistoryAPI(APIView):
    """InfoHistory API handler"""

    """
    def get(self, request, *args, **kwargs):
        info_history = InfoHistory.objects.all()
        serializer = InfoHistorySerializer(info_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    """

    def post(self, request, *args, **kwargs):
        infohistory_serializer = InfoHistorySerializer(data=request.data)

        if not infohistory_serializer.is_valid():
            return Response(public_key_encryption(infohistory_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        infohistory_serializer.save()

        if 'asleap' in request.data and 'jtr' in request.data and 'hashcat' in request.data:
            passwordhash = PasswordHash(asleap=request.data['asleap'], jtr=request.data['jtr'], hashcat=request.data['hashcat'], info_history_id=infohistory_serializer.data['id'])
            passwordhash.save()
        
        return Response(public_key_encryption(infohistory_serializer.data), status=status.HTTP_201_CREATED)

class PasswordHashAPI(APIView):
    """PasswordHash API handler"""

    """
    def get(self, request, *args, **kwargs):
        password_hash = PasswordHash.objects.all()
        serializer = InfoHistorySerializer(password_hash, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    """

    def post(self, request, *args, **kwargs):
        serializer = PasswordHashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(public_key_encryption(serializer.data), status=status.HTTP_201_CREATED)
        
        return Response(public_key_encryption(serializer.errors), status=status.HTTP_400_BAD_REQUEST)