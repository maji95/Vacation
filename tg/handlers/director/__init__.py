from telegram.ext import Application, CallbackQueryHandler
from .vacation_approval import approve_direct_vacation, reject_direct_vacation

def register_handlers(application: Application):
    """Регистрация обработчиков директора"""
    application.add_handler(CallbackQueryHandler(approve_direct_vacation, pattern="approve_direct_vacation"))
    application.add_handler(CallbackQueryHandler(reject_direct_vacation, pattern="reject_direct_vacation"))
