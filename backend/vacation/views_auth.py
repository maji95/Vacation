from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from datetime import datetime

# --- Аутентификация и регистрация ---

def user_login(request):
    """
    Аутентификация пользователя по имени и паролю
    """
    # ... (реализация переносится из views.py)
    pass

def user_register(request):
    """
    Регистрация нового пользователя
    """
    # ... (реализация переносится из views.py)
    pass

@csrf_protect
def login_view(request):
    """
    Обработка входа пользователя через HTML-форму
    """
    # ... (реализация переносится из views.py)
    pass
