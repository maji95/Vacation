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

async def department_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает отчеты по отделу"""
    logger.info("Executing department_reports function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права начальника отдела
        head = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not head or head.role.name != "Начальник отдела":
            await query.edit_message_text("У вас нет прав начальника отдела.")
            return

        # Создаем клавиатуру с типами отчетов
        keyboard = [
            [InlineKeyboardButton("Отпуска отдела", callback_data="department_vacation_report")],
            [InlineKeyboardButton("Статистика отдела", callback_data="department_stats")],
            [InlineKeyboardButton("« Назад", callback_data="department_head_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Отчеты отдела {head.department.name}:",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in department_reports: {e}")
        await query.edit_message_text("Произошла ошибка при открытии отчетов отдела.")
    finally:
        session.close()
        logger.info("department_reports function completed")
