"""
URL configuration for vacation_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from vacation import views as vacation_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('vacation.urls')),  # API endpoints
    
    # Web views
    path('', vacation_views.index, name='index'),
    path('submit/', vacation_views.submit, name='submit'),
    path('requests/', vacation_views.requests, name='requests'),
    path('calendar/', vacation_views.calendar_view, name='calendar_view'),
    path('vacations/', vacation_views.vacation_list, name='vacation_list'),
    path('vacations/<int:pk>/', vacation_views.vacation_detail, name='vacation_detail'),
    
    # Authentication
    path('login/', vacation_views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
