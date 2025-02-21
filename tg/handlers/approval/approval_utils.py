from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest, ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def check_approval_permissions(user: User, expected_name: str = None) -> bool:
    """
    Проверяет права пользователя на утверждение заявки
    :param user: Пользователь
    :param expected_name: Ожидаемое имя утверждающего (если есть)
    :return: bool
    """
    if not user:
        return False
    
    if expected_name and user.full_name != expected_name:
        return False
        
    return user.is_director or user.is_hr

async def notify_users(context: ContextTypes.DEFAULT_TYPE, chat_ids: list, message: str):
    """
    Отправляет уведомление списку пользователей
    """
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )
        except Exception as e:
            logger.error(f"Error sending notification to {chat_id}: {e}")

async def notify_hr_managers(context: ContextTypes.DEFAULT_TYPE, request_obj, approver_name: str = None):
    """
    Уведомляет HR-менеджеров об одобренном отпуске
    :param context: Контекст телеграм бота
    :param request_obj: Объект запроса (VacationRequest или ApprovalFirst/Second/Final)
    :param approver_name: Имя утверждающего (опционально)
    """
    session = get_session()
    try:
        hr_managers = session.query(User).filter_by(is_hr=True).all()
        
        # Определяем сотрудника в зависимости от типа объекта
        if hasattr(request_obj, 'user_id'):
            # Для VacationRequest
            employee = session.query(User).filter_by(id=request_obj.user_id).first()
        else:
            # Для ApprovalFirst/Second/Final
            employee = session.query(User).filter_by(full_name=request_obj.name).first()
            
        if not employee:
            logger.error(f"Employee not found for request: {request_obj}")
            return
        
        message = (
            f"✅ Новый одобренный отпуск\n"
            f"Сотрудник: {employee.full_name}\n"
            f"Период: {request_obj.start_date.strftime('%d.%m.%Y')} - "
            f"{request_obj.end_date.strftime('%d.%m.%Y')}"
        )
        
        if approver_name:
            message += f"\nОдобрил: {approver_name}"
        
        for hr in hr_managers:
            try:
                await context.bot.send_message(
                    chat_id=hr.telegram_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления HR {hr.full_name}: {e}")
    finally:
        session.close()

async def notify_employee_request(context: ContextTypes.DEFAULT_TYPE, vacation_request, is_approved: bool):
    """
    Уведомляет сотрудника о решении по его заявке (для VacationRequest объектов)
    """
    session = get_session()
    try:
        employee = session.query(User).filter_by(id=vacation_request.user_id).first()
        if not employee:
            return

        status_text = "одобрен" if is_approved else "отклонен"
        status_icon = "✅" if is_approved else "❌"
        message = (
            f"{status_icon} Ваш запрос на отпуск с {vacation_request.start_date.strftime('%d.%m.%Y')} "
            f"по {vacation_request.end_date.strftime('%d.%m.%Y')} {status_text}!"
        )

        await notify_users(context, [employee.telegram_id], message)
    finally:
        session.close()

async def notify_employee_approval(context: ContextTypes.DEFAULT_TYPE, approval_entry, is_approved: bool):
    """
    Уведомляет сотрудника о решении по его заявке (для Approval объектов, в которых поле user_id отсутствует,
    используется поле name для поиска сотрудника)
    """
    session = get_session()
    try:
        employee = session.query(User).filter_by(full_name=approval_entry.name).first()
        if not employee:
            return

        status_text = "одобрен" if is_approved else "отклонен"
        status_icon = "✅" if is_approved else "❌"
        message = (
            f"{status_icon} Ваш запрос на отпуск с {approval_entry.start_date.strftime('%d.%m.%Y')} "
            f"по {approval_entry.end_date.strftime('%d.%m.%Y')} {status_text}!"
        )

        await notify_users(context, [employee.telegram_id], message)
    finally:
        session.close()

async def update_vacation_status(session, vacation_request_id: int, new_status: str):
    """
    Обновляет статус заявки на отпуск
    """
    vacation_request = session.query(VacationRequest).filter_by(id=vacation_request_id).first()
    if vacation_request and vacation_request.status == 'pending':
        vacation_request.status = new_status
        session.commit()
        return vacation_request
    return None

async def create_done_approval(session, approval_entry, status: str):
    """
    Создает запись в таблице завершенных утверждений
    """
    done_approval = ApprovalDone(
        name=approval_entry.name,
        name_approval=approval_entry.name_approval,
        days=approval_entry.days,
        start_date=approval_entry.start_date,
        end_date=approval_entry.end_date,
        status=status
    )
    session.add(done_approval)
    session.commit()
    return done_approval
