from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, VacationRequest, ApprovalProcess, ApprovalFirst, ApprovalSecond, ApprovalFinal
from django.utils import timezone
from datetime import datetime

# --- Заявки на отпуск ---

def index(request):
    """
    Главная страница с информацией о пользователе и его отпусках
    """
    # ... (реализация переносится из views.py)
    pass

@login_required
def submit(request):
    """
    Страница подачи заявки на отпуск с многоуровневым согласованием
    """
    if request.method == 'POST':
        user = request.user
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        vacation_type = request.POST.get('vacation_type')
        comments = request.POST.get('comments')
        # Для HR/админа можно выбрать сотрудника вручную
        employee_id = request.POST.get('employee') or request.POST.get('user_id')
        if employee_id:
            user = User.objects.get(id=employee_id)
        
        # Находим процесс согласования по имени
        approval_proc = ApprovalProcess.objects.filter(original_name=user.full_name).first()
        if not approval_proc:
            messages.error(request, f'Для пользователя {user.full_name} не найден процесс согласования!')
            return render(request, 'submit.html', {'user': request.user})
        
        # Создаём заявку
        vac = VacationRequest.objects.create(
            user=user,
            start_date=start_date,
            end_date=end_date,
            vacation_type=vacation_type,
            status='pending',
            comments=comments
        )
        # Первый этап согласования
        ApprovalFirst.objects.create(
            vacation_request=vac,
            name=user.full_name,
            name_approval=approval_proc.first_approval,
            status='pending'
        )
        messages.success(request, 'Заявка успешно создана и отправлена на первое согласование!')
        return redirect('requests')
    else:
        employees = User.objects.all()
        return render(request, 'submit.html', {'user': request.user, 'employees': employees})

@login_required
def requests(request):
    """
    Страница просмотра всех заявок
    """
    # ... (реализация переносится из views.py)
    pass

@login_required
def vacation_list(request):
    """
    API для получения и создания заявок на отпуск
    """
    # ... (реализация переносится из views.py)
    pass

@login_required
def vacation_detail(request, pk):
    """
    API для обработки согласования заявки на каждом этапе
    """
    vac = get_object_or_404(VacationRequest, id=pk)
    user = request.user
    # Определяем текущий этап согласования
    approval_first = ApprovalFirst.objects.filter(vacation_request=vac).first()
    approval_second = ApprovalSecond.objects.filter(vacation_request=vac).first()
    approval_final = ApprovalFinal.objects.filter(vacation_request=vac).first()
    approval_proc = ApprovalProcess.objects.filter(original_name=vac.user.full_name).first()
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        # Первый этап
        if approval_first and approval_first.status == 'pending' and user.full_name == approval_first.name_approval:
            if action == 'approve':
                approval_first.status = 'approved'
                approval_first.comment = comment
                approval_first.save()
                # Создаём второй этап
                ApprovalSecond.objects.create(
                    vacation_request=vac,
                    name=vac.user.full_name,
                    name_approval=approval_proc.second_approval,
                    status='pending'
                )
                messages.success(request, 'Первое согласование пройдено!')
            elif action == 'reject':
                approval_first.status = 'rejected'
                approval_first.comment = comment
                approval_first.save()
                vac.status = 'rejected'
                vac.save()
                messages.error(request, 'Заявка отклонена на первом этапе.')
            return redirect('requests')
        # Второй этап
        if approval_second and approval_second.status == 'pending' and user.full_name == approval_second.name_approval:
            if action == 'approve':
                approval_second.status = 'approved'
                approval_second.comment = comment
                approval_second.save()
                # Создаём финальный этап
                ApprovalFinal.objects.create(
                    vacation_request=vac,
                    name=vac.user.full_name,
                    name_approval=approval_proc.final_approval,
                    status='pending'
                )
                messages.success(request, 'Второе согласование пройдено!')
            elif action == 'reject':
                approval_second.status = 'rejected'
                approval_second.comment = comment
                approval_second.save()
                vac.status = 'rejected'
                vac.save()
                messages.error(request, 'Заявка отклонена на втором этапе.')
            return redirect('requests')
        # Финальный этап
        if approval_final and approval_final.status == 'pending' and user.full_name == approval_final.name_approval:
            if action == 'approve':
                approval_final.status = 'approved'
                approval_final.comment = comment
                approval_final.save()
                vac.status = 'approved'
                vac.save()
                messages.success(request, 'Заявка полностью согласована!')
            elif action == 'reject':
                approval_final.status = 'rejected'
                approval_final.comment = comment
                approval_final.save()
                vac.status = 'rejected'
                vac.save()
                messages.error(request, 'Заявка отклонена на финальном этапе.')
            return redirect('requests')
    # Показываем детали заявки и статусы этапов
    context = {
        'vacation': vac,
        'approval_first': approval_first,
        'approval_second': approval_second,
        'approval_final': approval_final,
        'user': user
    }
    return render(request, 'vacation_detail.html', context)
