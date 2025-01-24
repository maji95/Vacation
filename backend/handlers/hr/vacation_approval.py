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

async def approve_vacation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Одобрение запроса на отпуск HR-ом"""
    logger.info("Executing approve_vacation_request function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права HR
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "HR":
            await query.edit_message_text("У вас нет прав HR.")
            return

        # Здесь будет логика одобрения отпуска
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="hr_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция одобрения отпуска HR-ом в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in approve_vacation_request: {e}")
        await query.edit_message_text("Произошла ошибка при одобрении отпуска.")
    finally:
        session.close()
        logger.info("approve_vacation_request function completed")

async def reject_vacation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклонение запроса на отпуск HR-ом"""
    logger.info("Executing reject_vacation_request function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права HR
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "HR":
            await query.edit_message_text("У вас нет прав HR.")
            return

        # Здесь будет логика отклонения отпуска
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="hr_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция отклонения отпуска HR-ом в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in reject_vacation_request: {e}")
        await query.edit_message_text("Произошла ошибка при отклонении отпуска.")
    finally:
        session.close()
        logger.info("reject_vacation_request function completed")
