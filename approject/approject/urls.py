"""
URL configuration for approject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# django admin imports
from django.contrib import admin
from django.urls import path

# app-specific imports
from apscavange import views

#####################################
#   URL Patterns                    #
#####################################

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_view, name="index"),
    path('login', views.LoginView.as_view(), name="login"),
    path('logout', views.logout_view, name="logout"),
    path('dashboard', views.DashboardView.as_view(), name="dashboard"),
    path('infrastructure', views.InfrastructureView.as_view(), name="infrastructure")
]
