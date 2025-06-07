from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest, ApprovalProcess, ApprovalFirst, ApprovalSecond, ApprovalFinal
from datetime import datetime
import logging
from .approval_handler import calculate_vacation_days

logger = logging.getLogger(__name__)

async def create_approval_request(vacation_request_id: int):
    """Создает запрос на утверждение в соответствующей таблице"""
    session = get_session()
    try:
        vacation_request = session.query(VacationRequest).get(vacation_request_id)
        employee = session.query(User).get(vacation_request.user_id)
        
        # Получаем процесс утверждения для сотрудника
        approval_process = session.query(ApprovalProcess).filter_by(
            employee_name=employee.full_name
        ).first()

        if approval_process:
            # Определяем цепочку утверждения
            chain = []
            if approval_process.first_approval:
                chain.append('first')
            if approval_process.second_approval:
                chain.append('second')
            if approval_process.final_approval:
                chain.append('final')
            
            if not chain:
                return False

            # Создаем первую запись в цепочке
            first_level = chain[0]
            new_approval = {
                'first': ApprovalFirst,
                'second': ApprovalSecond,
                'final': ApprovalFinal
            }[first_level](
                name=employee.full_name,
                name_approval=getattr(approval_process, f'{first_level}_approval'),
                days=calculate_vacation_days(vacation_request.start_date, vacation_request.end_date),
                start_date=vacation_request.start_date,
                end_date=vacation_request.end_date
            )
            
            session.add(new_approval)
            session.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Error creating approval request: {e}")
        return False
    finally:
        session.close()

async def send_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE, vacation_request_id: int):
    """Отправляет уведомление о новом запросе на утверждение"""
    session = get_session()
    try:
        # Получаем запрос на отпуск
        vacation_request = session.query(VacationRequest).get(vacation_request_id)
        if not vacation_request:
            return False

        # Получаем сотрудника
        employee = session.query(User).get(vacation_request.user_id)
        if not employee:
            return False

        # Получаем процесс утверждения
        approval_process = session.query(ApprovalProcess).filter_by(
            employee_name=employee.full_name
        ).first()

        if not approval_process:
            return False

        # Определяем первого утверждающего
        approver_name = None
        if approval_process.first_approval:
            approver_name = approval_process.first_approval
        elif approval_process.final_approval:
            approver_name = approval_process.final_approval

        if not approver_name:
            return False

        # Получаем утверждающего
        approver = session.query(User).filter_by(full_name=approver_name).first()
        if not approver:
            return False

        # Получаем запись утверждения
        approval_class = ApprovalFirst if approval_process.first_approval else ApprovalFinal
        approval_entry = session.query(approval_class).filter_by(
            name=employee.full_name,
            status='pending'
        ).first()

        if not approval_entry:
            return False

        # Отправляем уведомление утверждающему
        level = 'first' if approval_process.first_approval else 'final'
        keyboard = [
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{level}_{approval_entry.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{level}_{approval_entry.id}")
            ]
        ]
        text = (
            f"📋 Новый запрос на отпуск\n"
            f"От: {employee.full_name}\n"
            f"Период: {vacation_request.start_date.strftime('%d.%m.%Y')} - {vacation_request.end_date.strftime('%d.%m.%Y')}\n"
            f"Дней: {int(calculate_vacation_days(vacation_request.start_date, vacation_request.end_date))}"
        )
        
        await context.bot.send_message(
            chat_id=approver.telegram_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return True

    except Exception as e:
        logger.error(f"Error sending approval request: {e}")
        return False
    finally:
        session.close()

__all__ = ['create_approval_request', 'send_approval_request']
