from django.shortcuts import render, redirect
from django.views.generic import View   # django generic View class
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator # database objects paginator
from django.contrib.auth import authenticate, login, logout # import Django built in functions

from .models import Seizure, InfoHistory, PasswordHash#, User
from .forms import LoginForm, PageItemsSelectForm, SearchEmailForm

# Create your views here.

#####################################
#   Helper Functions                #
#####################################

def authentication_handler(request, auth_required=True):
    if auth_required:
        if not request.user.is_authenticated:
            request.session['auth_message'] = 'The specified page requires authentication.'
            return False

    request.session['auth_message'] = ""

    return True

def pagination_handler(request, search_email_form, page_items_select_form):
    """
    cur_page = request.GET.get('page', 1)
    try:
        cur_page = int(cur_page)
    except:
        cur_page = 1
    """

    # TODO: maybe ensure that when the items per page change, the current page resets or at least immediately
    #       changes to the maximum it can get

    cur_page = int(page_items_select_form.fields['cur_page'].initial)
    items_per_page = int(page_items_select_form.fields['page_items'].initial)

    if page_items_select_form.is_valid():
        cur_page = int(page_items_select_form.cleaned_data['cur_page'])
        items_per_page = int(page_items_select_form.cleaned_data['page_items'])

    objects = None

    # NOTE: objects type will depend on the selected table
    if search_email_form.is_valid():
        objects = Seizure.objects.filter(email__contains=search_email_form.cleaned_data['search_email'])
    else:
        objects = Seizure.objects.all()

    paginator = Paginator(objects, items_per_page)

    if (cur_page < paginator.page_range.start):
        cur_page = paginator.page_range.start
    elif (cur_page >= paginator.page_range.stop):
        cur_page = paginator.page_range.stop - 1

    table_data = {}
    table_data["items_start"] = (cur_page - 1) * items_per_page + 1
    table_data["items_stop"] = cur_page * items_per_page if cur_page * items_per_page < paginator.count else paginator.count
    table_data["items_count"] = paginator.count
    table_data["items_data"] = paginator.page(cur_page).object_list
    table_data["max_page"] = paginator.page_range.stop - 1
    table_data["columns"] = [f.name for f in Seizure._meta.get_fields() if not f.is_relation or f.one_to_one]

    return table_data

#####################################
#   View Classes                    #
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
        
        search_email_form = SearchEmailForm()
        page_items_select_form = PageItemsSelectForm()
        table_data = pagination_handler(request, search_email_form, page_items_select_form)
        
        return render(request, 'dashboard.html', {"table_data": table_data, "page_items_select_form": page_items_select_form, "search_email_form": search_email_form})

    def post(self, request):
        assert isinstance(request, HttpRequest)
        if not authentication_handler(request):
            return redirect('login')

        search_email_form = SearchEmailForm(request.POST)
        page_items_select_form = PageItemsSelectForm(request.POST)
        table_data = pagination_handler(request, search_email_form, page_items_select_form)

        # ajax request, return only the table html
        if (request.POST.get("ajaxTableUpdate") == "True"):
            return render(request, 'dashboard_table.html', {"table_data": table_data, "page_items_select_form": page_items_select_form, "search_email_form": search_email_form})
        
        return render(request, 'dashboard.html', {"table_data": table_data, "page_items_select_form": page_items_select_form, "search_email_form": search_email_form})
    
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
#   View Functions                  #
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