from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, HoursRequest, ApprovalProcess
from .approval_hours_utils import get_approval_chain, logger

async def send_hours_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: int):
    """
    Отправляет запрос на утверждение отгула следующему утверждающему в цепочке.
    """
    session = get_session()
    try:
        # Получаем запрос на отгул
        hours_request = session.query(HoursRequest).filter_by(id=request_id).first()
        if not hours_request:
            logger.error(f"Hours request not found: {request_id}")
            return False
            
        # Получаем сотрудника
        employee = session.query(User).filter_by(id=hours_request.user_id).first()
        if not employee:
            logger.error(f"Employee not found for user_id: {hours_request.user_id}")
            return False
            
        # Получаем процесс утверждения
        approval_process = session.query(ApprovalProcess).filter_by(employee_name=employee.full_name).first()
        if not approval_process:
            logger.error(f"Approval process not found for: {employee.full_name}")
            return False
            
        # Получаем цепочку утверждения
        chain = get_approval_chain(employee.full_name)
        
        # Определяем текущий уровень утверждения
        current_level = None
        for level in chain:
            approver_name = getattr(approval_process, f'{level}_approval')
            approver = session.query(User).filter_by(full_name=approver_name).first()
            
            if approver:
                current_level = level
                break
                
        if not current_level or not approver:
            logger.error("No approver found in chain")
            return False
            
        # Формируем сообщение
        message = (
            f"🔔 Новый запрос на отгул\n"
            f"От: {employee.full_name}\n"
            f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
            f"Время: {hours_request.start_hour} - {hours_request.end_hour}"
        )
        
        # Создаем клавиатуру
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Одобрить",
                    callback_data=f"approve_hours_{request_id}_{current_level}"
                ),
                InlineKeyboardButton(
                    "❌ Отклонить",
                    callback_data=f"reject_hours_{request_id}_{current_level}"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение утверждающему
        try:
            await context.bot.send_message(
                chat_id=approver.telegram_id,
                text=message,
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            logger.error(f"Error sending message to approver: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in send_hours_approval_request: {e}")
        return False
    finally:
        session.close()

__all__ = ['send_hours_approval_request']
