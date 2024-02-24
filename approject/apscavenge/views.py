from django.shortcuts import render, redirect

from django.views.generic import View   # django generic View class

from django.http import HttpRequest, HttpResponse

from .models import Seizure, InfoHistory, PasswordHash#, User

from .forms import LoginForm

# database objects paginator
from django.core.paginator import Paginator

# import Django built in functions
from django.contrib.auth import authenticate, login, logout

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
        
        p_data = None
        
        s = Seizure.objects.all()
        p = Paginator(s, 3)
        #print(p.count)
        #print(p.page_range)
        #print(p.page(1).object_list)

        p_data = p.page(1).object_list

        print(p_data)
        
        return render(request, 'dashboard.html', {"p_data": p_data})

    def post(self, request):
        assert isinstance(request, HttpRequest)
        
        return HttpResponse('Still nothing')
    
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
    
    dummy_count = 5

    for i in range(dummy_count):
        Seizure(email=f"dummyemail{i}@realm").save()

    for i in range(dummy_count):
        info_history = InfoHistory(user_type=f"Dummy Type {i}", user_info="No info provided.", area=f"Dummy Area {i}", seizure_email_id=f"dummyemail{i}@realm")
        info_history.save()

        if i % 2:
            print(f"Inserting password hash for info history object {info_history}")
            PasswordHash(asleap=f"asleap_dummy_hash_{info_history.id}", jtr=f"jtr_dummy_hash_{info_history.id}", hashcat=f"hashcat_dummy_hash_{info_history.id}", info_history_id=info_history.id).save()

    return HttpResponse('<h3>Dummy data inserted.<h3>')

def delete_dummy_data(request):
    """Delete dummy data from database"""
    assert isinstance(request, HttpRequest)
    if not authentication_handler(request):
        return HttpResponse('<h3>You must be authenticated.<h3>')
    
    Seizure.objects.all().delete()

    return HttpResponse('<h3>Dummy data deleted.<h3>')