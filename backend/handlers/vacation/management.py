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

async def vacation_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает панель управления отпусками"""
    logger.info("Executing vacation_management function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Здесь будет логика получения списка запросов на отпуск
        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Управление отпусками (в разработке)",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in vacation_management: {e}")
        await query.edit_message_text("Произошла ошибка при открытии управления отпусками.")
    finally:
        session.close()
        logger.info("vacation_management function completed")

async def approve_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Одобряет запрос на отпуск"""
    logger.info("Executing approve_vacation function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Здесь будет логика одобрения отпуска
        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="vacation_management")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция одобрения отпуска в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in approve_vacation: {e}")
        await query.edit_message_text("Произошла ошибка при одобрении отпуска.")
    finally:
        session.close()
        logger.info("approve_vacation function completed")

async def reject_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отклоняет запрос на отпуск"""
    logger.info("Executing reject_vacation function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Здесь будет логика отклонения отпуска
        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="vacation_management")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция отклонения отпуска в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in reject_vacation: {e}")
        await query.edit_message_text("Произошла ошибка при отклонении отпуска.")
    finally:
        session.close()
        logger.info("reject_vacation function completed")
