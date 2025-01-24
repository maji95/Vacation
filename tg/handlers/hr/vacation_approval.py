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

async def view_approved_vacations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр утвержденных отпусков"""
    logger.info("Executing view_approved_vacations function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права HR
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "HR":
            await query.edit_message_text("У вас нет прав HR.")
            return

        # Здесь будет логика отображения утвержденных отпусков
        # TODO: Добавить запрос к таблице утвержденных отпусков
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="hr_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция просмотра утвержденных отпусков в разработке\n"
            "Здесь будет отображаться список утвержденных отпусков начальниками отделов",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in view_approved_vacations: {e}")
        await query.edit_message_text("Произошла ошибка при загрузке утвержденных отпусков.")
    finally:
        session.close()
        logger.info("view_approved_vacations function completed")
