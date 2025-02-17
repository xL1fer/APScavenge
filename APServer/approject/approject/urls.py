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
from apserver import views

#####################################
#   URL Patterns                    #
#####################################

urlpatterns = [
    # django admin site url
    path('admin/', admin.site.urls),

    # custom views urls
    path('', views.index_view, name="index"),
    path('login', views.LoginView.as_view(), name="login"),
    path('logout', views.logout_view, name="logout"),
    path('dashboard', views.DashboardView.as_view(), name="dashboard"),
    path('dashboard-stats', views.DashboardStatsView.as_view(), name="dashboard-stats"),
    path('dashboard-users', views.DashboardUsersView.as_view(), name="dashboard-users"),
    path('infrastructure', views.InfrastructureView.as_view(), name="infrastructure"),
    path('infrastructure/<str:area>/', views.InfrastructureAgentView.as_view(), name="infrastructure-agent"),

    path('insertdummydata', views.insert_dummy_data, name="insertdummydata"),
    path('deletedummydata', views.delete_dummy_data, name="deletedummydata"),

    # api urls
    path('token-auth-api', views.CustomAuthToken.as_view(), name="custom-auth-token"),
    path('central-heartbeat-api', views.CentralHeartbeatAPI.as_view(), name="central-heartbeat-api"),
    path('seizure-api', views.SeizureAPI.as_view(), name="seizure-api"),
    path('infohistory-api', views.InfoHistoryAPI.as_view(), name="infohistory-api"),
    path('passwordhash-api', views.PasswordHashAPI.as_view(), name="passwordhash-api"),
]
