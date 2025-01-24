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

async def hr_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает отчеты для HR"""
    logger.info("Executing hr_reports function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права HR
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "HR":
            await query.edit_message_text("У вас нет прав HR.")
            return

        # Создаем клавиатуру с типами отчетов
        keyboard = [
            [InlineKeyboardButton("Отчет по больничным", callback_data="hr_report_sick")],
            [InlineKeyboardButton("Отчет по отпускам", callback_data="hr_report_vacation")],
            [InlineKeyboardButton("« Назад", callback_data="hr_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Выберите тип отчета:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in hr_reports: {e}")
        await query.edit_message_text("Произошла ошибка при открытии отчетов HR.")
    finally:
        session.close()
        logger.info("hr_reports function completed")
