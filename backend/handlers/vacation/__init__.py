from telegram.ext import CallbackQueryHandler, MessageHandler, filters

from .request import vacation_request, vacation_by_days, vacation_by_hours
from .management import vacation_management, approve_vacation, reject_vacation
from .message_handler import handle_message

def register(application):
    """Регистрация всех обработчиков для отпусков"""
    # Обработчики запроса отпуска
    application.add_handler(CallbackQueryHandler(vacation_request, pattern="vacation_request"))
    application.add_handler(CallbackQueryHandler(vacation_by_days, pattern="vacation_by_days"))
    application.add_handler(CallbackQueryHandler(vacation_by_hours, pattern="vacation_by_hours"))
    
    # Обработчики управления отпусками
    application.add_handler(CallbackQueryHandler(vacation_management, pattern="vacation_management"))
    application.add_handler(CallbackQueryHandler(approve_vacation, pattern="approve_vacation"))
    application.add_handler(CallbackQueryHandler(reject_vacation, pattern="reject_vacation"))
    
    # Обработчик сообщений для отпусков
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
