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

async def view_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню отчетов"""
    logger.info("Executing view_reports function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права директора
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "Директор":
            await query.edit_message_text("У вас нет прав директора.")
            return

        # Создаем клавиатуру с типами отчетов
        keyboard = [
            [InlineKeyboardButton("Отчет по отпускам", callback_data="generate_report_vacation")],
            [InlineKeyboardButton("Отчет по отделам", callback_data="generate_report_department")],
            [InlineKeyboardButton("« Назад", callback_data="director_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Выберите тип отчета:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in view_reports: {e}")
        await query.edit_message_text("Произошла ошибка при открытии меню отчетов.")
    finally:
        session.close()
        logger.info("view_reports function completed")

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерирует выбранный отчет"""
    logger.info("Executing generate_report function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права директора
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "Директор":
            await query.edit_message_text("У вас нет прав директора.")
            return

        # Здесь будет логика генерации отчетов
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="view_reports")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция генерации отчетов в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in generate_report: {e}")
        await query.edit_message_text("Произошла ошибка при генерации отчета.")
    finally:
        session.close()
        logger.info("generate_report function completed")
