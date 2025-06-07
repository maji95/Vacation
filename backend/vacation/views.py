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
import logging
from .models import User, VacationRequest
from django.views.decorators.csrf import csrf_protect

# Настройка логирования
logger = logging.getLogger(__name__)

# Общая функция для подготовки контекста для всех представлений
def get_common_context(request):
    """
    Возвращает общий контекст для всех представлений
    """
    # Проверяем, аутентифицирован ли пользователь
    if request.user.is_authenticated:
        # Используем данные аутентифицированного пользователя
        user = request.user
        
        # Получаем все заявки на отпуск из базы данных
        vacation_requests = []
        
        # Если пользователь имеет права HR, директора или админа, показываем все заявки
        if user.is_hr or user.is_director or user.is_admin:
            all_requests = VacationRequest.objects.all().order_by('-created_at')
        else:
            # Иначе показываем только заявки текущего пользователя
            all_requests = VacationRequest.objects.filter(user=user).order_by('-created_at')
        
        # Преобразуем заявки в формат для шаблона
        for req in all_requests:
            # Проверяем тип данных перед вызовом метода date()
            start_date = req.start_date
            if hasattr(start_date, 'date'):
                start_date = start_date.date()
                
            end_date = req.end_date
            if hasattr(end_date, 'date'):
                end_date = end_date.date()
                
            vacation_requests.append({
                'id': req.id,
                'user': {'id': req.user.id, 'full_name': req.user.full_name},
                'start_date': start_date,
                'end_date': end_date,
                'vacation_type': req.vacation_type,
                'status': req.status,
                'comments': req.comments or ''
            })
        
        # Получаем список всех сотрудников для HR, директоров и админов
        employees = []
        if user.is_hr or user.is_director or user.is_admin:
            all_users = User.objects.all().order_by('full_name')
            for emp in all_users:
                employees.append({
                    'id': emp.id,
                    'full_name': emp.full_name
                })
    else:
        # Создаем тестовые данные для просмотра шаблонов, если пользователь не аутентифицирован
        class MockUser:
            def __init__(self):
                self.id = 1
                self.full_name = "Тестовый Пользователь"
                self.vacation_days = 20
                self.is_hr = True
                self.is_director = False
                self.is_admin = False
        
        user = MockUser()
        
        # Тестовые данные для заявок на отпуск
        vacation_requests = [
            {
                'id': 1,
                'user': {'id': 1, 'full_name': 'Тестовый Пользователь'},
                'start_date': date(2025, 5, 1),
                'end_date': date(2025, 5, 15),
                'vacation_type': 'annual',
                'status': 'pending',
                'comments': 'Плановый отпуск'
            },
            {
                'id': 2,
                'user': {'id': 2, 'full_name': 'Петров Петр'},
                'start_date': date(2025, 6, 10),
                'end_date': date(2025, 6, 24),
                'vacation_type': 'annual',
                'status': 'approved',
                'comments': 'Летний отпуск'
            },
            {
                'id': 3,
                'user': {'id': 3, 'full_name': 'Сидоров Сидор'},
                'start_date': date(2025, 7, 5),
                'end_date': date(2025, 7, 10),
                'vacation_type': 'unpaid',
                'status': 'rejected',
                'comments': 'Семейные обстоятельства'
            }
        ]
        
        # Тестовые данные для сотрудников
        employees = [
            {'id': 1, 'full_name': 'Тестовый Пользователь'},
            {'id': 2, 'full_name': 'Петров Петр'},
            {'id': 3, 'full_name': 'Сидоров Сидор'}
        ]
    
    # Базовый контекст, который будет доступен на всех страницах
    context = {
        'user': user,
        'vacation_requests': vacation_requests,
        'employees': employees,
    }
    
    return context

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
            'error': 'Пожалуйста, укажите имя и пароль'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Используем authenticate для проверки учетных данных
        user = authenticate(request, username=full_name, password=password)

        if user is not None:
            # Если аутентификация успешна, выполняем вход
            login(request, user)
            return Response({
                'message': 'Вход выполнен успешно',
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
                'error': 'Неверное имя пользователя или пароль'
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'error': f'Ошибка при входе: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

def login_view(request):
    """
    Обработка входа пользователя через HTML-форму
    """
    if request.method == 'POST':
        # Логируем все POST данные для отладки
        logger.info(f"POST данные: {request.POST}")
        
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        
        logger.info(f"Попытка входа: full_name={full_name}, password_length={len(password) if password else 0}")
        
        if not full_name or not password:
            logger.warning("Отсутствует имя пользователя или пароль")
            return render(request, 'login.html', {'form_errors': 'Пожалуйста, укажите имя и пароль'})
        
        try:
            # Используем authenticate для проверки учетных данных
            logger.info(f"Вызов authenticate с параметрами: full_name={full_name}")
            user = authenticate(request, full_name=full_name, password=password)
            
            logger.info(f"Результат authenticate: user={user}")
            
            if user is not None:
                # Если аутентификация успешна, выполняем вход
                login(request, user)
                
                # Логирование успешной аутентификации
                logger.info(f'Пользователь {full_name} успешно авторизован')
                
                # Перенаправляем на страницу, указанную в параметре next, или на главную
                next_url = request.POST.get('next') or '/'
                return redirect(next_url)
            else:
                # Логирование неудачной аутентификации
                logger.warning(f'Пользователь {full_name} не авторизован. Неверное имя пользователя или пароль')
                return render(request, 'login.html', {'form_errors': 'Неверное имя пользователя или пароль'})
        except Exception as e:
            # Логирование ошибки при входе
            logger.error(f'Ошибка при входе пользователя {full_name}: {str(e)}')
            return render(request, 'login.html', {'form_errors': f'Ошибка при входе: {str(e)}'})
    
    # Если метод GET, просто отображаем форму входа
    return render(request, 'login.html', {'next': request.GET.get('next', '/')})

@login_required
def index(request):
    """
    Главная страница с информацией о пользователе и его отпусках
    """
    context = get_common_context(request)
    
    # Добавляем специфичные для этой страницы данные, если нужно
    context['title'] = 'Главная страница'
    
    return render(request, 'index.html', context)

@login_required
def submit(request):
    """
    Страница подачи заявки на отпуск
    """
    context = get_common_context(request)
    
    # Добавляем специфичные для этой страницы данные
    context['title'] = 'Подача заявки на отпуск'
    
    # Обработка отправки формы
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            vacation_type = request.POST.get('vacation_type')
            comments = request.POST.get('comments', '')
            
            # Проверяем, что все обязательные поля заполнены
            if not all([start_date_str, end_date_str, vacation_type]):
                context['error_message'] = 'Пожалуйста, заполните все обязательные поля'
                return render(request, 'submit.html', context)
            
            # Преобразуем строки дат в объекты date (не datetime)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Проверяем, что дата начала не в прошлом
            today = date.today()
            if start_date < today:
                context['error_message'] = 'Дата начала отпуска не может быть в прошлом'
                return render(request, 'submit.html', context)
            
            # Проверяем, что дата окончания не раньше даты начала
            if end_date < start_date:
                context['error_message'] = 'Дата окончания отпуска не может быть раньше даты начала'
                return render(request, 'submit.html', context)
            
            # Вычисляем количество дней отпуска
            vacation_days = (end_date - start_date).days + 1
            
            # Определяем пользователя (для HR, директора или админа может быть выбран другой сотрудник)
            user_id = request.POST.get('employee')
            user = request.user  # По умолчанию используем текущего пользователя
            
            if request.user.is_hr or request.user.is_director or request.user.is_admin:
                if user_id:
                    # Если выбран другой сотрудник, находим его в базе данных
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        context['error_message'] = 'Выбранный сотрудник не найден'
                        return render(request, 'submit.html', context)
            
            # Проверяем, есть ли у пользователя достаточно дней отпуска
            # (только для ежегодного оплачиваемого отпуска)
            if vacation_type == 'annual' and vacation_days > user.vacation_days:
                context['error_message'] = f'У сотрудника недостаточно дней отпуска. Доступно: {user.vacation_days}, запрошено: {vacation_days}'
                return render(request, 'submit.html', context)
            
            # Создаем запись в базе данных
            vacation_request = VacationRequest(
                user=user,
                start_date=start_date,
                end_date=end_date,
                vacation_type=vacation_type,
                status='pending',
                comments=comments
            )
            vacation_request.save()
            
            # Если это ежегодный оплачиваемый отпуск, вычитаем дни из доступных
            if vacation_type == 'annual':
                user.vacation_days -= vacation_days
                user.save()
            
            # Добавляем сообщение об успешном создании заявки
            context['success_message'] = 'Заявка на отпуск успешно создана и отправлена на рассмотрение'
            
            # Обновляем контекст с новыми данными
            return render(request, 'submit.html', get_common_context(request))
            
        except Exception as e:
            # Логируем ошибку и показываем сообщение пользователю
            logger.error(f"Error in submit view: {e}")
            context['error_message'] = f'Произошла ошибка при обработке заявки: {str(e)}. Пожалуйста, попробуйте еще раз'
    
    return render(request, 'submit.html', context)

@login_required
def requests(request):
    """
    Страница просмотра всех заявок
    """
    context = get_common_context(request)
    
    # Добавляем специфичные для этой страницы данные
    context['title'] = 'Все заявки на отпуск'
    
    # Фильтрация заявок по статусу, если указан в GET-параметрах
    status_filter = request.GET.get('status', '')
    if status_filter:
        context['vacation_requests'] = [r for r in context['vacation_requests'] if r['status'] == status_filter]
    
    # Фильтрация заявок по сотруднику, если указан в GET-параметрах
    user_id_filter = request.GET.get('user_id', '')
    if user_id_filter and user_id_filter.isdigit():
        user_id = int(user_id_filter)
        context['vacation_requests'] = [r for r in context['vacation_requests'] if r['user']['id'] == user_id]
    
    return render(request, 'requests.html', context)

@login_required
def calendar_view(request):
    """
    Страница календаря отпусков
    """
    context = get_common_context(request)
    
    # Определяем текущий месяц и год или берем из параметров запроса
    today = date.today()
    month_param = request.GET.get('month', '')
    
    if month_param:
        try:
            year, month = map(int, month_param.split('-'))
            current_date = date(year, month, 1)
        except (ValueError, IndexError):
            current_date = date(today.year, today.month, 1)
    else:
        current_date = date(today.year, today.month, 1)
    
    # Получаем первый и последний день месяца
    year = current_date.year
    month = current_date.month
    _, last_day = calendar.monthrange(year, month)
    
    # Создаем список дней месяца
    month_days = []
    first_day_weekday = current_date.weekday()
    
    # Добавляем пустые ячейки в начало для выравнивания по дням недели
    for _ in range(first_day_weekday):
        month_days.append({'day': None, 'is_weekend': False, 'vacations': []})
    
    # Добавляем дни месяца
    for day in range(1, last_day + 1):
        current_day = date(year, month, day)
        is_weekend = current_day.weekday() >= 5  # 5 и 6 - это суббота и воскресенье
        
        # Находим отпуска на этот день
        day_vacations = []
        for vacation in context['vacation_requests']:
            if vacation['start_date'] <= current_day <= vacation['end_date']:
                day_vacations.append(vacation)
        
        month_days.append({
            'day': day,
            'date': current_day,
            'is_weekend': is_weekend,
            'vacations': day_vacations
        })
    
    # Получаем название месяца
    month_names = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    month_name = month_names[month - 1]
    
    # Вычисляем предыдущий и следующий месяцы для навигации
    prev_month_date = current_date - timedelta(days=1)
    prev_month = f"{prev_month_date.year}-{prev_month_date.month}"
    
    next_month_date = date(year, month, last_day) + timedelta(days=1)
    next_month = f"{next_month_date.year}-{next_month_date.month}"
    
    # Добавляем данные календаря в контекст
    context.update({
        'title': 'Календарь отпусков',
        'month_days': month_days,
        'month_name': month_name,
        'year': year,
        'prev_month': prev_month,
        'next_month': next_month
    })
    
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
