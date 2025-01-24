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

async def manage_employees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает панель управления сотрудниками"""
    logger.info("Executing manage_employees function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права HR
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "HR":
            await query.edit_message_text("У вас нет прав HR.")
            return

        # Получаем список сотрудников
        employees = session.query(User).all()
        
        message = "Управление сотрудниками:\n\n"
        keyboard = []
        
        for emp in employees:
            dept_name = emp.department.name if emp.department else "Без отдела"
            message += f"👤 {emp.full_name} ({dept_name})\n"
            keyboard.append([InlineKeyboardButton(f"Изменить {emp.full_name}", callback_data=f"edit_employee_{emp.id}")])
        
        keyboard.append([InlineKeyboardButton("Добавить сотрудника", callback_data="add_employee")])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="hr_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_employees: {e}")
        await query.edit_message_text("Произошла ошибка при открытии управления сотрудниками.")
    finally:
        session.close()
        logger.info("manage_employees function completed")

async def add_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление нового сотрудника"""
    logger.info("Executing add_employee function")
    query = update.callback_query
    await query.answer()

    # Здесь будет логика добавления сотрудника
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_employees")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Функция добавления сотрудника в разработке",
        reply_markup=reply_markup
    )
    logger.info("add_employee function completed")

async def edit_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактирование сотрудника"""
    logger.info("Executing edit_employee function")
    query = update.callback_query
    await query.answer()

    # Здесь будет логика редактирования сотрудника
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_employees")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Функция редактирования сотрудника в разработке",
        reply_markup=reply_markup
    )
    logger.info("edit_employee function completed")

async def delete_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление сотрудника"""
    logger.info("Executing delete_employee function")
    query = update.callback_query
    await query.answer()

    # Здесь будет логика удаления сотрудника
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_employees")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Функция удаления сотрудника в разработке",
        reply_markup=reply_markup
    )
    logger.info("delete_employee function completed")
