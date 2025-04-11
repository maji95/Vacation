from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date
from calendar import monthrange
import calendar
from .models import User, VacationRequest

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

# Web views for templates

# @login_required
def index_view(request):
    """
    Главная страница с информацией о пользователе и его отпусках
    """
    # Создаем тестовые данные для просмотра шаблона
    class MockUser:
        def __init__(self):
            self.full_name = "Тестовый Пользователь"
            self.vacation_days = 20
            self.is_hr = True
            self.is_director = False
            self.is_admin = False
    
    mock_user = MockUser()
    
    # Создаем тестовые заявки
    class MockVacationRequest:
        def __init__(self, id, start_date, end_date, status, vacation_type, user):
            self.id = id
            self.start_date = start_date
            self.end_date = end_date
            self.status = status
            self.vacation_type = vacation_type
            self.user = user
            self.comments = "Комментарий к заявке"
            self.created_at = timezone.now()
    
    # Создаем несколько тестовых заявок
    user_requests = [
        MockVacationRequest(1, timezone.now() + timedelta(days=10), timezone.now() + timedelta(days=20), 'pending', 'annual', mock_user),
        MockVacationRequest(2, timezone.now() + timedelta(days=30), timezone.now() + timedelta(days=40), 'approved', 'annual', mock_user)
    ]
    
    pending_requests = [
        MockVacationRequest(3, timezone.now() + timedelta(days=5), timezone.now() + timedelta(days=15), 'pending', 'unpaid', mock_user),
        MockVacationRequest(4, timezone.now() + timedelta(days=25), timezone.now() + timedelta(days=35), 'pending', 'study', mock_user)
    ]
    
    context = {
        'user': mock_user,
        'vacation_requests': user_requests,
        'pending_requests': pending_requests,
    }
    
    return render(request, 'index.html', context)

# @login_required
def submit_view(request):
    """
    Страница подачи заявки на отпуск
    """
    # Создаем тестовые данные для просмотра шаблона
    class MockUser:
        def __init__(self):
            self.full_name = "Тестовый Пользователь"
            self.vacation_days = 20
            self.is_hr = True
            self.is_director = False
            self.is_admin = False
    
    mock_user = MockUser()
    
    # Создаем тестовый список сотрудников
    employees = [
        {'id': 1, 'full_name': 'Иванов Иван'},
        {'id': 2, 'full_name': 'Петров Петр'},
        {'id': 3, 'full_name': 'Сидоров Сидор'}
    ]
    
    context = {
        'user': mock_user,
        'employees': employees,
    }
    
    return render(request, 'submit.html', context)

# @login_required
def requests_view(request):
    """
    Страница просмотра всех заявок
    """
    # Создаем тестовые данные для просмотра шаблона
    class MockUser:
        def __init__(self):
            self.full_name = "Тестовый Пользователь"
            self.vacation_days = 20
            self.is_hr = True
            self.is_director = False
            self.is_admin = False
            self.id = 1
    
    mock_user = MockUser()
    
    # Создаем тестовые заявки
    class MockVacationRequest:
        def __init__(self, id, start_date, end_date, status, vacation_type, user):
            self.id = id
            self.start_date = start_date
            self.end_date = end_date
            self.status = status
            self.vacation_type = vacation_type
            self.user = user
            self.comments = "Комментарий к заявке"
            self.created_at = timezone.now()
    
    # Создаем несколько тестовых заявок
    vacation_requests = [
        MockVacationRequest(1, timezone.now() + timedelta(days=10), timezone.now() + timedelta(days=20), 'pending', 'annual', mock_user),
        MockVacationRequest(2, timezone.now() + timedelta(days=30), timezone.now() + timedelta(days=40), 'approved', 'annual', mock_user),
        MockVacationRequest(3, timezone.now() + timedelta(days=5), timezone.now() + timedelta(days=15), 'pending', 'unpaid', mock_user),
        MockVacationRequest(4, timezone.now() + timedelta(days=25), timezone.now() + timedelta(days=35), 'rejected', 'study', mock_user)
    ]
    
    # Создаем тестовый список сотрудников
    employees = [
        {'id': 1, 'full_name': 'Иванов Иван'},
        {'id': 2, 'full_name': 'Петров Петр'},
        {'id': 3, 'full_name': 'Сидоров Сидор'}
    ]
    
    context = {
        'user': mock_user,
        'vacation_requests': vacation_requests,
        'employees': employees,
    }
    
    return render(request, 'requests.html', context)

# @login_required
def calendar_view(request):
    """
    Страница календаря отпусков
    """
    # Создаем тестовые данные для просмотра шаблона
    class MockUser:
        def __init__(self):
            self.full_name = "Тестовый Пользователь"
            self.vacation_days = 20
            self.is_hr = True
            self.is_director = False
            self.is_admin = False
    
    mock_user = MockUser()
    
    # Определяем текущий месяц и год или берем из параметров запроса
    today = date.today()
    month_param = request.GET.get('month', '')
    
    if month_param:
        try:
            # Формат month_param: 'YYYY-MM'
            year, month = map(int, month_param.split('-'))
            current_date = date(year, month, 1)
        except (ValueError, TypeError):
            current_date = date(today.year, today.month, 1)
    else:
        current_date = date(today.year, today.month, 1)
    
    # Получаем предыдущий и следующий месяцы
    if current_date.month == 1:
        prev_month = f"{current_date.year - 1}-12"
    else:
        prev_month = f"{current_date.year}-{current_date.month - 1:02d}"
    
    if current_date.month == 12:
        next_month = f"{current_date.year + 1}-01"
    else:
        next_month = f"{current_date.year}-{current_date.month + 1:02d}"
    
    # Получаем название месяца
    month_name = calendar.month_name[current_date.month]
    
    # Получаем количество дней в месяце
    _, num_days = monthrange(current_date.year, current_date.month)
    
    # Получаем день недели для первого дня месяца (0 - понедельник, 6 - воскресенье)
    first_day_weekday = current_date.weekday()
    
    # Создаем тестовые заявки на отпуск
    class MockVacationRequest:
        def __init__(self, id, start_date, end_date, status, vacation_type, user):
            self.id = id
            self.start_date = start_date
            self.end_date = end_date
            self.status = status
            self.vacation_type = vacation_type
            self.user = user
            self.comments = "Комментарий к заявке"
            self.created_at = timezone.now()
    
    # Создаем несколько тестовых заявок на отпуск в текущем месяце
    test_vacation_requests = [
        MockVacationRequest(
            1, 
            datetime(current_date.year, current_date.month, 10), 
            datetime(current_date.year, current_date.month, 20), 
            'approved', 
            'annual', 
            mock_user
        ),
        MockVacationRequest(
            2, 
            datetime(current_date.year, current_date.month, 5), 
            datetime(current_date.year, current_date.month, 15), 
            'pending', 
            'unpaid', 
            mock_user
        )
    ]
    
    # Создаем календарь
    calendar_data = []
    
    # Добавляем пустые ячейки для дней до начала месяца
    for _ in range(first_day_weekday):
        calendar_data.append({
            'day': '',
            'vacations': []
        })
    
    # Добавляем дни месяца
    for day in range(1, num_days + 1):
        day_date = date(current_date.year, current_date.month, day)
        
        # Проверяем, есть ли отпуска на этот день
        day_vacations = []
        for vacation in test_vacation_requests:
            vacation_start = vacation.start_date.date()
            vacation_end = vacation.end_date.date()
            
            if vacation_start <= day_date <= vacation_end:
                day_vacations.append({
                    'id': vacation.id,
                    'user': vacation.user.full_name,
                    'status': vacation.status,
                    'type': vacation.vacation_type
                })
        
        calendar_data.append({
            'day': day,
            'vacations': day_vacations,
            'is_weekend': day_date.weekday() >= 5  # 5 и 6 - суббота и воскресенье
        })
    
    # Разбиваем календарь на недели
    weeks = []
    for i in range(0, len(calendar_data), 7):
        weeks.append(calendar_data[i:i+7])
    
    context = {
        'user': mock_user,
        'calendar_data': weeks,
        'month_name': month_name,
        'year': current_date.year,
        'prev_month': prev_month,
        'next_month': next_month,
        'current_month': f"{current_date.year}-{current_date.month:02d}"
    }
    
    return render(request, 'calendar.html', context)

@login_required
def vacation_list(request):
    """
    API для получения и создания заявок на отпуск
    """
    if request.method == 'POST':
        # Создание новой заявки
        user_id = request.POST.get('user_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        vacation_type = request.POST.get('vacation_type')
        comments = request.POST.get('comments', '')
        
        # Проверка данных
        if not all([user_id, start_date, end_date, vacation_type]):
            messages.error(request, 'Все поля должны быть заполнены')
            return redirect('submit')
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_date > end_date:
                messages.error(request, 'Дата начала не может быть позже даты окончания')
                return redirect('submit')
            
            # Проверяем, имеет ли пользователь право создавать заявку для другого сотрудника
            if str(request.user.id) != user_id and not (request.user.is_hr or request.user.is_director or request.user.is_admin):
                messages.error(request, 'У вас нет прав для создания заявки от имени другого сотрудника')
                return redirect('submit')
            
            # Создаем заявку
            user = User.objects.get(id=user_id)
            vacation = VacationRequest.objects.create(
                user=user,
                start_date=start_date,
                end_date=end_date,
                vacation_type=vacation_type,
                comments=comments,
                status='pending'
            )
            
            messages.success(request, 'Заявка успешно создана')
            return redirect('requests')
            
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
            return redirect('submit')
        except Exception as e:
            messages.error(request, f'Ошибка при создании заявки: {str(e)}')
            return redirect('submit')
    
    # GET запрос - возвращаем список заявок
    return redirect('requests')

@login_required
def vacation_detail(request, pk):
    """
    API для получения, обновления и удаления заявки на отпуск
    """
    vacation = get_object_or_404(VacationRequest, pk=pk)
    
    if request.method == 'POST':
        # Проверяем права доступа
        if not (request.user.is_hr or request.user.is_director or request.user.is_admin):
            messages.error(request, 'У вас нет прав для изменения статуса заявки')
            return redirect('requests')
        
        action = request.POST.get('action')
        
        if action == 'approve':
            vacation.status = 'approved'
            vacation.save()
            messages.success(request, f'Заявка #{vacation.id} одобрена')
        elif action == 'reject':
            vacation.status = 'rejected'
            vacation.save()
            messages.success(request, f'Заявка #{vacation.id} отклонена')
        
        return redirect('requests')
    
    # GET запрос - возвращаем детали заявки
    context = {
        'vacation': vacation
    }
    
    return render(request, 'vacation_detail.html', context)
