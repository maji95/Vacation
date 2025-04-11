from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    
    # Web views
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('requests/', views.requests, name='requests'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    
    # Vacation request endpoints
    path('vacations/', views.vacation_list, name='vacation_list'),
    path('vacations/<int:pk>/', views.vacation_detail, name='vacation_detail'),
]
