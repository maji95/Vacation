from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from .models import User

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """
    Аутентификация пользователя по имени и паролю
    """
    full_name = request.data.get('full_name')
    password = request.data.get('password')

    if not full_name or not password:
        return Response({
            'error': 'Please provide both full name and password'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=full_name, password=password)

    if user is not None:
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': {
                'full_name': user.full_name,
                'vacation_days': user.vacation_days,
                'is_hr': user.is_hr,
                'is_director': user.is_director,
                'is_admin': user.is_admin
            }
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    """
    Регистрация нового пользователя
    """
    full_name = request.data.get('full_name')
    password = request.data.get('password', '1234')  # Если пароль не указан, используем '1234'

    if not full_name:
        return Response({
            'error': 'Full name is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Проверяем, что имя содержит как минимум два слова
    if len(full_name.split()) < 2:
        return Response({
            'error': 'Full name must include both first and last name'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Проверяем, не существует ли уже пользователь с таким именем
    if User.objects.filter(full_name=full_name).exists():
        return Response({
            'error': 'User with this name already exists'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(
            full_name=full_name,
            password=password
        )
        return Response({
            'message': 'User created successfully',
            'user': {
                'full_name': user.full_name,
                'vacation_days': user.vacation_days
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
