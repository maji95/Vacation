from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, Department
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def view_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику по отпускам и отделам"""
    logger.info("Executing view_statistics function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права директора
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "Директор":
            await query.edit_message_text("У вас нет прав директора.")
            return

        # Получаем статистику по отделам
        departments = session.query(Department).all()
        
        message = "📊 Статистика по отделам:\n\n"
        
        for dept in departments:
            # Подсчитываем количество сотрудников в отделе
            employee_count = session.query(User).filter_by(department_id=dept.id).count()
            
            # Подсчитываем общее количество дней отпуска в отделе
            total_vacation_days = session.query(User).filter_by(department_id=dept.id).with_entities(
                func.sum(User.vacation_days)
            ).scalar() or 0
            
            message += f"📁 {dept.name}:\n"
            message += f"   Сотрудников: {employee_count}\n"
            message += f"   Всего дней отпуска: {total_vacation_days}\n"
            message += f"   Среднее кол-во дней: {total_vacation_days/employee_count if employee_count > 0 else 0:.1f}\n\n"

        # Добавляем кнопку возврата
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="director_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in view_statistics: {e}")
        await query.edit_message_text("Произошла ошибка при получении статистики.")
    finally:
        session.close()
        logger.info("view_statistics function completed")
