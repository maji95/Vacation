from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def view_vacation_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр всех заявок на отпуск"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем, что пользователь является директором
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or not user.is_director:
            await query.edit_message_text("У вас нет прав для просмотра заявок.")
            return

        # Получаем все pending заявки
        pending_requests = session.query(VacationRequest).filter_by(status='pending').all()

        if not pending_requests:
            keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
            await query.edit_message_text(
                "На данный момент нет заявок на рассмотрение.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Формируем сообщение со списком заявок
        message_text = "📋 Заявки на рассмотрение:\n\n"
        keyboard = []

        for request in pending_requests:
            message_text += (
                f"От: {request.user.full_name}\n"
                f"Период: {request.start_date.strftime('%d.%m.%Y')} - {request.end_date.strftime('%d.%m.%Y')}\n"
                f"Статус: {request.status}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_vacation_{request.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_vacation_{request.id}")
            ])

        keyboard.append([InlineKeyboardButton("« В главное меню", callback_data="show_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in view_vacation_requests: {e}")
        await query.edit_message_text("Произошла ошибка при получении списка заявок.")
    finally:
        session.close()
