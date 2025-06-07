from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest
import logging
from ..approval.approval_utils import check_approval_permissions

logger = logging.getLogger(__name__)

async def view_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список запросов на отпуск для директора"""
    query = update.callback_query
    await query.answer()
    
    session = get_session()
    try:
        # Проверяем права директора
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not await check_approval_permissions(user):
            await query.edit_message_text("У вас нет прав для просмотра запросов.")
            return
        
        # Получаем все активные запросы
        requests = session.query(VacationRequest).filter_by(status='pending').all()
        
        if not requests:
            keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
            await query.edit_message_text(
                "На данный момент нет активных запросов на отпуск.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        # Формируем сообщение со списком запросов
        message = "📋 Активные запросы на отпуск:\n\n"
        keyboard = []
        
        for req in requests:
            employee = session.query(User).filter_by(id=req.user_id).first()
            message += (
                f"👤 {employee.full_name}\n"
                f"📅 {req.start_date.strftime('%d.%m.%Y')} - {req.end_date.strftime('%d.%m.%Y')}\n"
                f"📊 Дней: {req.days}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton("✅", callback_data=f"approve_vacation_{req.id}"),
                InlineKeyboardButton("❌", callback_data=f"reject_vacation_{req.id}")
            ])
        
        keyboard.append([InlineKeyboardButton("« В главное меню", callback_data="show_menu")])
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Error viewing requests: {e}")
        await query.edit_message_text("Произошла ошибка при получении списка запросов.")
    finally:
        session.close()
