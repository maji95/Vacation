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

async def manage_departments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает панель управления отделами"""
    logger.info("Executing manage_departments function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права директора
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.role.name != "Директор":
            await query.edit_message_text("У вас нет прав директора.")
            return

        # Получаем список отделов
        departments = session.query(Department).all()
        
        # Формируем сообщение и клавиатуру
        message = "Управление отделами:\n\n"
        keyboard = []
        
        for dept in departments:
            message += f"📁 {dept.name}\n"
            keyboard.append([InlineKeyboardButton(f"Изменить {dept.name}", callback_data=f"edit_department_{dept.id}")])
        
        keyboard.append([InlineKeyboardButton("Добавить отдел", callback_data="add_department")])
        keyboard.append([InlineKeyboardButton("« Назад", callback_data="director_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_departments: {e}")
        await query.edit_message_text("Произошла ошибка при открытии управления отделами.")
    finally:
        session.close()
        logger.info("manage_departments function completed")

async def add_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление нового отдела"""
    logger.info("Executing add_department function")
    query = update.callback_query
    await query.answer()

    # Здесь будет логика добавления отдела
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_departments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Функция добавления отдела в разработке",
        reply_markup=reply_markup
    )
    logger.info("add_department function completed")

async def edit_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактирование отдела"""
    logger.info("Executing edit_department function")
    query = update.callback_query
    await query.answer()

    # Здесь будет логика редактирования отдела
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_departments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Функция редактирования отдела в разработке",
        reply_markup=reply_markup
    )
    logger.info("edit_department function completed")

async def delete_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление отдела"""
    logger.info("Executing delete_department function")
    query = update.callback_query
    await query.answer()

    # Здесь будет логика удаления отдела
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_departments")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Функция удаления отдела в разработке",
        reply_markup=reply_markup
    )
    logger.info("delete_department function completed")
