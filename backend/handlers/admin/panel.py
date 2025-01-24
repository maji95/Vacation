from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, RegistrationQueue
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает админ-панель с информацией о новых пользователях и кнопками управления"""
    logger.info("Executing admin_panel function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or not user.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Получаем количество пользователей в очереди регистрации
        new_users_count = session.query(RegistrationQueue).count()

        # Создаем клавиатуру с кнопками управления
        keyboard = [
            [InlineKeyboardButton("Новые пользователи", callback_data="new_users")],
            [InlineKeyboardButton("Добавить пользователя", callback_data="add_user")],
            [InlineKeyboardButton("Удалить пользователей", callback_data="delete_users")],
            [InlineKeyboardButton("Список пользователей", callback_data="list_users")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Панель администратора\n\n"
            f"Новых пользователей в очереди: {new_users_count}",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in admin_panel: {e}")
        await query.edit_message_text("Произошла ошибка при открытии панели администратора.")
    finally:
        session.close()
        logger.info("admin_panel function completed")
