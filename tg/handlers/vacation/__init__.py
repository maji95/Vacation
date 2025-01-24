from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler
from .message_handler import handle_message
from .request import (
    vacation_request, 
    vacation_by_days, 
    vacation_by_hours,
    back_to_menu,
    restart_vacation_request,
    switch_to_hours
)

def register_handlers(application: Application):
    """Регистрация обработчиков отпусков"""
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчики callback'ов
    application.add_handler(CallbackQueryHandler(vacation_request, pattern="vacation_request"))
    application.add_handler(CallbackQueryHandler(vacation_by_days, pattern="vacation_by_days"))
    application.add_handler(CallbackQueryHandler(vacation_by_hours, pattern="vacation_by_hours"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="back_to_menu"))
    application.add_handler(CallbackQueryHandler(restart_vacation_request, pattern="restart_vacation_request"))
    application.add_handler(CallbackQueryHandler(switch_to_hours, pattern="switch_to_hours"))
