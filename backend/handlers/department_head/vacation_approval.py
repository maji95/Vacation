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

async def approve_team_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Одобрение запроса на отпуск сотрудника отдела"""
    logger.info("Executing approve_team_vacation function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права начальника отдела
        head = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not head or head.role.name != "Начальник отдела":
            await query.edit_message_text("У вас нет прав начальника отдела.")
            return

        # Здесь будет логика одобрения отпуска
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_team")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция одобрения отпуска сотрудника в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in approve_team_vacation: {e}")
        await query.edit_message_text("Произошла ошибка при одобрении отпуска.")
    finally:
        session.close()
        logger.info("approve_team_vacation function completed")

async def reject_team_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклонение запроса на отпуск сотрудника отдела"""
    logger.info("Executing reject_team_vacation function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права начальника отдела
        head = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not head or head.role.name != "Начальник отдела":
            await query.edit_message_text("У вас нет прав начальника отдела.")
            return

        # Здесь будет логика отклонения отпуска
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_team")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция отклонения отпуска сотрудника в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in reject_team_vacation: {e}")
        await query.edit_message_text("Произошла ошибка при отклонении отпуска.")
    finally:
        session.close()
        logger.info("reject_team_vacation function completed")
