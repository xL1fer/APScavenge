from django.shortcuts import render, redirect

from django.views.generic import View   # django generic View class

from django.http import HttpRequest, HttpResponse

from .models import Seizure, InfoHistory, PasswordHash#, User

from .forms import LoginForm

# import Django built in functions
from django.contrib.auth import authenticate, login, logout

# Create your views here.

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
        
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # get "username" and "password" using the cleaned_data method after form validation
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)

                return redirect('index')

        return render(request, 'login.html', {'login_form': login_form, 'login_message': 'Invalid user credentials.'})

class DashboardView(View):
    """Dashboard page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        
        return render(request, 'dashboard.html')

    def post(self, request):
        assert isinstance(request, HttpRequest)
        
        return HttpResponse('Still nothing')
    
class InfrastructureView(View):
    """Dashboard page render handler"""

    def get(self, request):
        assert isinstance(request, HttpRequest)
        
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
    
    return render(request, 'index.html')

def logout_view(request):
    """Logout request handler"""
    assert isinstance(request, HttpRequest)

    logout(request)
    return redirect('index')