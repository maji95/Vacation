from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает главное меню"""
    logger.info("Executing show_menu function")
    query = update.callback_query
    await query.answer()

    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton("Запрос отпуска", callback_data="vacation_request")],
        [InlineKeyboardButton("Управление отпусками", callback_data="vacation_management")],
        [InlineKeyboardButton("Панель администратора", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Выберите действие:",
        reply_markup=reply_markup
    )
    logger.info("show_menu function completed")

def register(application):
    """Регистрация всех обработчиков"""
    from .role_check import check_role
    from .admin import register as register_admin
    from .vacation import register as register_vacation
    from .director import register as register_director
    from .hr import register as register_hr
    from .department_head import register as register_department_head
    
    # Регистрируем основные команды
    application.add_handler(CommandHandler("start", check_role))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="show_menu"))
    
    # Регистрируем обработчики отпуска
    register_vacation(application)
    
    # Регистрируем обработчики админ-панели
    register_admin(application)
    
    # Регистрируем обработчики для разных ролей
    register_director(application)
    register_hr(application)
    register_department_head(application)
