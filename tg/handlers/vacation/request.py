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
    """Начало запроса отпуска"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            await query.edit_message_text("Пользователь не найден.")
            return

        keyboard = [
            [InlineKeyboardButton("По дням", callback_data="vacation_by_days")],
            [InlineKeyboardButton("По часам", callback_data="vacation_by_hours")],
            [InlineKeyboardButton("« Назад", callback_data="show_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💡 У вас доступно {user.vacation_days} дней отпуска.\n\n"
            "Выберите тип отпуска:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in vacation_request: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()

async def vacation_by_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отпуска по дням"""
    logger.info("Executing vacation_by_days function")
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("« Назад", callback_data="vacation_request")]]
    await query.edit_message_text(
        "Введите дату начала отпуска в формате ДД.ММ.ГГГГ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['vacation_state'] = 'waiting_start_date'

async def vacation_by_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отпуска по часам"""
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("« Назад", callback_data="vacation_request")]]
    await query.edit_message_text(
        "Введите дату и время начала отпуска в формате:\n"
        "ДД.ММ.ГГГГ ЧЧ:ММ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['vacation_state'] = 'waiting_hours'

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в предыдущее меню"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем состояние
    context.user_data.clear()
    
    # Возвращаемся к выбору типа отпуска
    await vacation_request(update, context)

async def restart_vacation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезапуск запроса отпуска"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем состояние
    context.user_data.clear()
    
    # Возвращаемся к запросу отпуска по дням
    await vacation_by_days(update, context)

async def switch_to_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключение на отпуск по часам"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем состояние
    context.user_data.clear()
    
    # Переходим к запросу отпуска по часам
    await vacation_by_hours(update, context)
