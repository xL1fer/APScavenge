from django.shortcuts import render, redirect

from django.views.generic import View   # django generic View class

from django.http import HttpRequest, HttpResponse

from .models import Seizure, InfoHistory, PasswordHash#, User

from .forms import LoginForm

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
        
        return render(request, 'dashboard.html')

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