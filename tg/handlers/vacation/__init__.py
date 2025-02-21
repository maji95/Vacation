from telegram.ext import CallbackQueryHandler, MessageHandler, filters
from .request import (
    vacation_request, 
    vacation_by_days,
    back_to_menu,
    restart_vacation_request,
    confirm_vacation
)
from .message_handler import handle_message
import logging

logger = logging.getLogger(__name__)

def register_handlers(application):
    """Регистрация обработчиков для отпусков"""
    logger.info("Регистрируем обработчики отпуска")
    
    # Основные обработчики
    application.add_handler(CallbackQueryHandler(vacation_request, pattern="vacation_request"))
    application.add_handler(CallbackQueryHandler(vacation_by_days, pattern="vacation_by_days"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="back_to_menu"))
    application.add_handler(CallbackQueryHandler(restart_vacation_request, pattern="restart_vacation_request"))
    application.add_handler(CallbackQueryHandler(confirm_vacation, pattern="confirm_vacation"))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r'^(\d{2}\.\d{2}\.\d{4})$'),
        handle_message
    ))
    
    logger.info("Обработчики отпуска зарегистрированы")
