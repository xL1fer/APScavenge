from django.shortcuts import render, redirect
from django.views.generic import View   # django generic View class
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator # database objects paginator
from django.contrib.auth import authenticate, login, logout # import Django built in functions

from .models import Seizure, InfoHistory, PasswordHash#, User
from .forms import LoginForm, PageItemsSelectForm, SelectTableForm, SearchTableForm

# Create your views here.

from django.template.defaulttags import register

#####################################
# Custom Django Template Filters    #
#####################################

@register.filter
def get_value(dictionary, key):
    return getattr(dictionary, key)

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
        if not search_table_form.is_valid():
            search_table_form = SearchTableForm()
        page_items_select_form = PageItemsSelectForm(request.POST)
        if not page_items_select_form.is_valid():
            page_items_select_form = PageItemsSelectForm()

        model_class = get_model_class(request, select_table_form, 'requestModel')
        table_data = table_data_handler(request, model_class, select_table_form, search_table_form, page_items_select_form)

        # ajax request, return only a sub portion of the dashboard content
        if request.POST.get("ajaxTableUpdate"):
            if request.POST.get('ajaxSubTableUpdate'):
                return render(request, 'dashboard_subtable.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})
            
            return render(request, 'dashboard_table.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})
        
        return render(request, 'dashboard.html', {"table_data": table_data, "select_table_form": select_table_form, "search_table_form": search_table_form, "page_items_select_form": page_items_select_form})
    
class InfrastructureView(View):
    """Dashboard page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')
        
        return render(request, 'infrastructure.html')

    def post(self, request):
        assert isinstance(request, HttpRequest)

        return HttpResponse('Still nothing')

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
    
    dummy_count = 50

    for i in range(dummy_count):
        Seizure(email=f"dummy{i}@realm").save()

    for i in range(dummy_count):
        info_history = InfoHistory(user_type=f"Dummy Type {i}", user_info="No info provided.", area=f"Dummy Area {i}", seizure_email_id=f"dummy{i}@realm")
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