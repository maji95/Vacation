from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает форму добавления нового пользователя"""
    logger.info("Executing add_user function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Добавляем кнопку возврата в админ-панель
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция добавления пользователей в разработке.",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in add_user: {e}")
        await query.edit_message_text("Произошла ошибка при открытии формы добавления пользователя.")
    finally:
        session.close()
        logger.info("add_user function completed")
