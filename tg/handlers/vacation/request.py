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

async def vacation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик запроса отпуска"""
    logger.info("Executing vacation_request function")
    query = update.callback_query
    await query.answer()

    # Создаем клавиатуру с выбором типа отпуска
    keyboard = [
        [InlineKeyboardButton("По дням", callback_data="vacation_by_days")],
        [InlineKeyboardButton("По часам", callback_data="vacation_by_hours")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Выберите тип отпуска:",
        reply_markup=reply_markup
    )
    logger.info("vacation_request function completed")

async def vacation_by_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отпуска по дням"""
    logger.info("Executing vacation_by_days function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Получаем информацию о пользователе
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            await query.edit_message_text("Пользователь не найден.")
            return

        await query.edit_message_text(
            f"У вас доступно {user.vacation_days} дней отпуска.\n"
            "Введите даты начала и конца отпуска в формате:\n"
            "ДД.ММ.ГГГГ - ДД.ММ.ГГГГ"
        )
        # Сохраняем состояние в контексте пользователя
        context.user_data['vacation_state'] = 'waiting_days'

    except Exception as e:
        logger.error(f"Error in vacation_by_days: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()
        logger.info("vacation_by_days function completed")

async def vacation_by_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отпуска по часам"""
    logger.info("Executing vacation_by_hours function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Получаем информацию о пользователе
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            await query.edit_message_text("Пользователь не найден.")
            return

        await query.edit_message_text(
            f"У вас доступно {user.vacation_days * 8} часов отпуска.\n"
            "Введите дату и количество часов в формате:\n"
            "ДД.ММ.ГГГГ 4"
        )
        # Сохраняем состояние в контексте пользователя
        context.user_data['vacation_state'] = 'waiting_hours'

    except Exception as e:
        logger.error(f"Error in vacation_by_hours: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()
        logger.info("vacation_by_hours function completed")
