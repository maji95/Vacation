from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, RegistrationQueue
import logging

logger = logging.getLogger(__name__)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает админ-панель с информацией о новых пользователях"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.full_name
    logger.info(f"Администратор {username} (ID: {user_id}) открыл админ-панель")
    
    await query.answer()

    session = get_session()
    try:
        # Получаем количество пользователей в очереди регистрации
        new_users_count = session.query(RegistrationQueue).count()

        # Формируем сообщение
        message = "👋 Панель администратора\n\n"
        message += f"📝 Новых заявок на регистрацию: {new_users_count}\n"

        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("Просмотреть заявки", callback_data="new_users")],
            [InlineKeyboardButton("« Назад", callback_data="show_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при загрузке админ-панели: {e}")
        await query.edit_message_text("Произошла ошибка при загрузке панели администратора.")
    finally:
        session.close()
