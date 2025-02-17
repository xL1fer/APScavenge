from django.shortcuts import render, redirect
from django.views.generic import View   # django generic View class
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator # database objects paginator
from django.contrib.auth import authenticate, login, logout # import Django built in functions

from django.db.models import Q
from .models import Seizure, InfoHistory, PasswordHash, AgentStatus#, User
from .forms import LoginForm, PageItemsSelectForm, SelectTableForm, SearchTableForm, SelectForm
from .serializers import SeizureSerializer, InfoHistorySerializer, PasswordHashSerializer, AgentStatusSerializer
from .tasks import init_tasks

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.template.defaulttags import register

from django.utils import timezone

from datetime import datetime, timedelta

import requests
import json

#from asgiref.sync import sync_to_async

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import load_pem_x509_certificate

from apserver.emailparser import emailparser

# Create your views here.

# Initialize background tasks
init_tasks()

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

g_action_start = 1 << 0
g_action_stop = 1 << 1
g_action_clear = 1 << 2
g_action_await = 1 << 3

g_parsing_email = False

#####################################
# Custom Django Template Filters    #
#####################################

@register.filter
def get_value(dictionary, key):
    return getattr(dictionary, key)

@register.filter
def mult(value1, value2):
    return value1 * value2

@register.filter
def bitwise_and(value1, value2):
    return value1 & value2

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

        # NOTE: Since the search_table_form.filter_field select has no default values, as they are only set directly in the dashboard_data_table.html template,
        #       we need to set them here, otherwise the form is considered invalid for containing values that do not correspond to any default
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

        relation_field = table_data["relation_fields"][-1]
        filter_params = {f"{relation_field}__{prev_model_class._meta.pk.name}": request.POST.get('requestValue')}
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

def to_int(arg):
    return int(arg) if is_int(arg) else None

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
            print("(ERROR) APServer: Decrypted text is not a valid json format")
    
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
    """Dashboard tables page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        select_table_form = SelectTableForm()
        search_table_form = SearchTableForm()
        page_items_select_form = PageItemsSelectForm()

        model_class = get_model_class(request, select_table_form, 'requestModel')
        table_data = table_data_handler(request, model_class, select_table_form, search_table_form, page_items_select_form)
        
        return render(request, 'dashboard_data.html', {'table_data': table_data, 'select_table_form': select_table_form, 'search_table_form': search_table_form, 'page_items_select_form': page_items_select_form})

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
                return render(request, 'dashboard_data_subtable.html', {'table_data': table_data, 'select_table_form': select_table_form, 'search_table_form': search_table_form, 'page_items_select_form': page_items_select_form})
            
            return render(request, 'dashboard_data_table.html', {'table_data': table_data, 'select_table_form': select_table_form, 'search_table_form': search_table_form, 'page_items_select_form': page_items_select_form})
        
        return render(request, 'dashboard_data.html', {'table_data': table_data, 'select_table_form': select_table_form, 'search_table_form': search_table_form, 'page_items_select_form': page_items_select_form})
    
def areas_stats_handler(area='_global_'):
    areas_stats = {area : {'ratio':[], 'captures':[], 'timely':[[], [], [], []]}}
    #areas_stats = {area : {'ratio':[], 'captures':[], 'timely':[[], [], [], []]} for area in InfoHistory.objects.values_list('area', flat=True).distinct()}

    for area in areas_stats:
        # emails with at least one associated passwordhash
        vulnerable_emails = InfoHistory.objects.filter(Q(area=area) if area != '_global_' else Q(), passwordhash__isnull=False).values_list('seizure_email__email', flat=True).distinct()
        vulnerable_num = len(vulnerable_emails)

        # emails without any associated passwordhash for the current area
        secure_emails = [email for email in InfoHistory.objects.filter(Q(area=area) if area != '_global_' else Q(), passwordhash__isnull=True).values_list('seizure_email__email', flat=True).distinct() if email not in vulnerable_emails]
        secure_num = len(secure_emails)

        # add the results to the dictionary
        areas_stats[area]['ratio'] = [secure_num, vulnerable_num]

        infohistory_objects = InfoHistory.objects.filter(Q(area=area) if area != '_global_' else Q()).order_by('capture_time').reverse()[:10]
        for infohistory in infohistory_objects:
            password_hash = None
            try:
                password_hash = infohistory.passwordhash
            except PasswordHash.DoesNotExist:
                pass

            time_past = (timezone.now() - infohistory.capture_time).total_seconds() / 60
            time_descriptor = 'minute'
            if time_past > 60:
                time_past /= 60
                time_descriptor = 'hour'
                if time_past > 24:
                    time_past /= 24
                    time_descriptor = 'day'
            areas_stats[area]['captures'].append([f"Capture {infohistory.id}", "Vulnerable" if password_hash else "Secure", f"{time_past:.2f} {time_descriptor}(s) ago"])
        
        cur_time = timezone.now()
        for i in range(1, 7):
            time_ago = cur_time - timedelta(days=i)
            time_range = cur_time - timedelta(days=i - 1)
            
            info_history_secure_count = InfoHistory.objects.filter(Q(area=area) if area != '_global_' else Q(), passwordhash__isnull=True, capture_time__gte=time_ago, capture_time__lte=time_range).count()
            info_history_vulnerable_count = InfoHistory.objects.filter(Q(area=area) if area != '_global_' else Q(), passwordhash__isnull=False, capture_time__gte=time_ago, capture_time__lte=time_range).count()

            areas_stats[area]['timely'][0].append(f"{i} day(s) ago")
            areas_stats[area]['timely'][1].append(info_history_secure_count + info_history_vulnerable_count)
            areas_stats[area]['timely'][2].append(info_history_secure_count)
            areas_stats[area]['timely'][3].append(info_history_vulnerable_count)

    return areas_stats

class DashboardStatsView(View):
    """Dashboard stats page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        select_stats_area_form = SelectForm()

        available_areas = ['_global_']
        available_areas.extend(list(InfoHistory.objects.values_list('area', flat=True).distinct()))
 
        return render(request, 'dashboard_stats.html', {'select_stats_area_form': select_stats_area_form, 'areas_stats': areas_stats_handler(), 'available_areas': available_areas})
    
    def post(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        if request.POST.get('ajaxStatsUpdate'):
            return render(request, 'dashboard_stats_area.html', {'areas_stats': areas_stats_handler(request.POST.get('filter_select'))})
        
        select_stats_area_form = SelectForm()

        available_areas = ['_global_']
        available_areas.extend(list(InfoHistory.objects.values_list('area', flat=True).distinct()))

        return render(request, 'dashboard_stats.html', {'select_stats_area_form': select_stats_area_form, 'areas_stats': areas_stats_handler(), 'available_areas': available_areas})

def users_info_handler(cur_page=None, search_field=None, filter_select=None):
    users_info = []
    items_per_page = 12
    if cur_page == None:
        cur_page = 1

    #filter_params = {f"email__contains": search_field if search_field is not None else ''}
    filter_params = {}
    if filter_select is not None and filter_select != 'all':
        filter_params['infohistory__passwordhash__isnull'] = False

    seizures = Seizure.objects.filter(**filter_params).distinct()
    if filter_select == 'secure':
        seizures = Seizure.objects.exclude(pk__in=seizures).distinct()

    if search_field is not None and search_field != '':
        seizures = seizures.filter(email__contains=search_field).distinct()

    paginator = Paginator(seizures, items_per_page)


    if cur_page < paginator.page_range.start:
        cur_page = paginator.page_range.start
    elif cur_page >= paginator.page_range.stop:
        cur_page = paginator.page_range.stop - 1

    grid_max_page = paginator.page_range.stop - 1

    for seizure in paginator.page(cur_page).object_list:
        if InfoHistory.objects.filter(seizure_email__email=seizure.email, passwordhash__isnull=False).exists():
            users_info.append([seizure.email, "Vulnerable", seizure.user_data])
        else:
            users_info.append([seizure.email, "Secure", seizure.user_data])

    return [users_info, cur_page, grid_max_page]

class DashboardUsersView(View):
    """Dashboard users page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        global g_parsing_email
        
        select_type_form = SelectForm()
        search_grid_form = SearchTableForm()
        
        return render(request, 'dashboard_users.html', {'users_info': users_info_handler(), 'select_type_form': select_type_form, 'search_grid_form': search_grid_form, "parsing_email": g_parsing_email})
    
    def post(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        global g_parsing_email
        
        select_type_form = SelectForm(request.POST)
        filter_select = request.POST.get('filter_select')
        valid_choices = ['all', 'secure', 'vulnerable']
        if filter_select in valid_choices:    # Ensure that filter_select is not forged
            select_type_form.fields['filter_select'].choices = [(filter_select, filter_select)]

        search_grid_form = SearchTableForm(request.POST)
        search_field = request.POST.get('search_field')

        if request.POST.get('ajaxPaginatorUpdate'):
            return render(request, 'dashboard_users_grid.html', {'users_info': users_info_handler(to_int(request.POST.get('cur_page')), search_field, filter_select), 'select_type_form': select_type_form, 'search_grid_form': search_grid_form, 'parsing_email': g_parsing_email})
        
        if request.POST.get('ajaxGridUpdate'):
            if not g_parsing_email:
                g_parsing_email = True
                seizure = Seizure.objects.get(email=request.POST.get('userEmail'))
                seizure.user_data = emailparser.parse_email(request.POST.get('userEmail'))
                seizure.save()
                g_parsing_email = False

            return render(request, 'dashboard_users_grid.html', {'users_info': users_info_handler(to_int(request.POST.get('cur_page')), search_field, filter_select), 'select_type_form': select_type_form, 'search_grid_form': search_grid_form, 'parsing_email': g_parsing_email})

        return render(request, 'dashboard_users.html', {'users_info': users_info_handler(to_int(request.POST.get('cur_page')), search_field, filter_select), 'select_type_form': select_type_form, 'search_grid_form': search_grid_form, 'parsing_email': g_parsing_email})

class InfrastructureView(View):
    """Infrastructure page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        update_active_agents()
        agentstatus_objects = AgentStatus.objects.all()
        
        return render(request, 'infrastructure.html', {'agentstatus_objects': agentstatus_objects})

    def post(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        global g_action_start, g_action_stop, g_action_await
        
        update_active_agents()
        agentstatus_objects = AgentStatus.objects.all()

        if request.POST.get('agentAction'):
            agentAction = request.POST['agentAction'].split('-')
            if is_int(agentAction[0]) and AgentStatus.objects.filter(id=agentAction[0]).exists():
                agentstatus = AgentStatus.objects.get(id=agentAction[0])

                if agentstatus.pending_request & g_action_start or agentstatus.pending_request & g_action_stop or agentstatus.pending_request & g_action_await:
                    for agent in agentstatus_objects:
                        if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                            agent.message = "Pending request."

                if agentAction[1] == 'start':
                    agentstatus.pending_request |= g_action_start
                elif agentAction[1] == 'stop':
                    agentstatus.pending_request |= g_action_stop
                agentstatus.save()

                """
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
                    for agent in agentstatus_objects:
                        if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                            agent.message = "Pending request."
                """
                
        if request.POST.get('ajaxGridUpdate'):
            return render(request, 'infrastructure_grid.html', {'agentstatus_objects': agentstatus_objects})

        return render(request, 'infrastructure.html', {'agentstatus_objects': agentstatus_objects})
    
'''
class InfrastructureView(View):
    """Infrastructure page render handler"""

    async def get(self, request):
        assert isinstance(request, HttpRequest)
        if not await sync_to_async(authentication_handler)(request):
            return redirect('login')

        await sync_to_async(update_active_agents)()
        agentstatus_objects = [agentstatus async for agentstatus in AgentStatus.objects.all()]
        
        return render(request, 'infrastructure.html', {"agentstatus_objects": agentstatus_objects})

    async def post(self, request):
        assert isinstance(request, HttpRequest)
        if not await sync_to_async(authentication_handler)(request):
            return redirect('login')
        
        await sync_to_async(update_active_agents)()
        agentstatus_objects = [agentstatus async for agentstatus in AgentStatus.objects.all()]

        if request.POST.get('agentAction'):
            agentAction = request.POST['agentAction'].split('-')
            if is_int(agentAction[0]) and await sync_to_async(AgentStatus.objects.filter(id=agentAction[0]).exists)():
                agentstatus = await sync_to_async(AgentStatus.objects.get)(id=agentAction[0])
                # Ensure we are not already performing a request to this agent
                if not agentstatus.is_requesting:
                    agentstatus.is_requesting = True
                    await sync_to_async(agentstatus.save)()
                    
                    if agentAction[1] == 'start':
                        try:
                            url = f'http://{agentstatus.ip}/start-attack-api'
                            response = await sync_to_async(requests.post)(url, json=public_key_encryption({"id": int(agentAction[0])}))
                            #print(f'Response: status code {response.status_code} | content {response.content}')

                            if response.status_code == 200:
                                agentstatus.is_attacking = True
                            await sync_to_async(agentstatus.save)()
                            agentstatus_objects = [agentstatus async for agentstatus in AgentStatus.objects.all()]

                            for agent in agentstatus_objects:
                                if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                                    try:
                                        agent.message = private_key_decryption(json.loads(response.content.decode("UTF-8")))['message']
                                        if agent.message == "Wrong agent id.":
                                            await sync_to_async(agentstatus.delete)()
                                    except ValueError as e:
                                        pass

                        except requests.exceptions.RequestException as e:
                            await sync_to_async(agentstatus.delete)()

                    elif agentAction[1] == 'stop':
                        try:
                            url = f'http://{agentstatus.ip}/stop-attack-api'
                            response = await sync_to_async(requests.post)(url, json=public_key_encryption({"id": int(agentAction[0])}))
                            #print(f'Response: status code {response.status_code} | content {response.content}')

                            agentstatus.is_attacking = False
                            await sync_to_async(agentstatus.save)()
                            agentstatus_objects = [agentstatus async for agentstatus in AgentStatus.objects.all()]

                            for agent in agentstatus_objects:
                                if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                                    try:
                                        agent.message = private_key_decryption(json.loads(response.content.decode("UTF-8")))['message']
                                        if agent.message == "Wrong agent id.":
                                            await sync_to_async(agentstatus.delete)()
                                    except ValueError as e:
                                        pass

                        except requests.exceptions.RequestException as e:
                            await sync_to_async(agentstatus.delete)()
                    
                    if await sync_to_async(AgentStatus.objects.filter(id=agentAction[0]).exists)():
                        agentstatus.is_requesting = False
                        await sync_to_async(agentstatus.save)()
                else:
                    for agent in agentstatus_objects:
                        if is_int(agentAction[0]) and int(agentAction[0]) == agent.id:
                            agent.message = "Pending request."
                
        if request.POST.get('ajaxGridUpdate'):
            return render(request, 'infrastructure_grid.html', {"agentstatus_objects": agentstatus_objects})

        return render(request, 'infrastructure.html', {"agentstatus_objects": agentstatus_objects})
'''

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
                agent_seizures.setdefault(infohistory.seizure_email.email, []).append([f"Capture {infohistory.id}", "Vulnerable" if password_hash else "Secure", time_past])

            agent_seizures = sorted(agent_seizures.items(), key=lambda x: min(info[2] for info in x[1]))

            return render(request, 'infrastructure_agent.html', {'agentstatus': agentstatus, 'agent_seizures': agent_seizures})
        
        return redirect('infrastructure')

    def post(self, request, area):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        global g_action_clear
        
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
                    agentstatus.pending_request |= g_action_clear
                    agentstatus.save()
                    """
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
                    """
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
        info_history = InfoHistory(area=f"dummy", seizure_email_id=f"dummy{i}@realm")
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
                pending_request = agentstatus.pending_request
                if agentstatus.pending_request & 1 or agentstatus.pending_request & 2:
                    agentstatus.pending_request = 0 | g_action_await
                else:
                    agentstatus.pending_request = 0
                agentstatus.save()

                return Response(public_key_encryption({'last_heartbeat': str(agentstatus.last_heartbeat), 'pending_request': pending_request}), status=status.HTTP_200_OK)
            else:
                return Response(public_key_encryption({'message': 'Wrong area agent id.'}), status=status.HTTP_400_BAD_REQUEST)

        serializer = AgentStatusSerializer(data=plain_data)
        if serializer.is_valid():
            serializer.save()
            return Response(public_key_encryption(serializer.data), status=status.HTTP_201_CREATED)
        
        """
        else:
            serializer = AgentStatusSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(public_key_encryption(serializer.data), status=status.HTTP_201_CREATED)
        """

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
        plain_data = private_key_decryption(request.data)

        if 'email' in plain_data and Seizure.objects.filter(email=plain_data['email']).exists():
            #seizure = Seizure.objects.get(email=plain_data['email'])
            return Response(public_key_encryption({'message': 'Email already registered.'}), status=status.HTTP_200_OK)

        serializer = SeizureSerializer(data=plain_data)
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
        plain_data = private_key_decryption(request.data)

        infohistory_serializer = InfoHistorySerializer(data=plain_data)

        if not infohistory_serializer.is_valid():
            return Response(public_key_encryption(infohistory_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        infohistory_serializer.save()

        if 'asleap' in plain_data and plain_data['asleap'] is not None and 'jtr' in plain_data and plain_data['jtr'] is not None and 'hashcat' in plain_data and plain_data['hashcat'] is not None:
            passwordhash = PasswordHash(asleap=plain_data['asleap'], jtr=plain_data['jtr'], hashcat=plain_data['hashcat'], info_history_id=infohistory_serializer.data['id'])
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
        plain_data = private_key_decryption(request.data)

        serializer = PasswordHashSerializer(data=plain_data)
        if serializer.is_valid():
            serializer.save()
            return Response(public_key_encryption(serializer.data), status=status.HTTP_201_CREATED)
        
        return Response(public_key_encryption(serializer.errors), status=status.HTTP_400_BAD_REQUEST)