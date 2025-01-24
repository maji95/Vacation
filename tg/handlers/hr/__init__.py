from telegram.ext import Application, CallbackQueryHandler
from .vacation_approval import view_approved_vacations

def register_handlers(application: Application):
    """Регистрация обработчиков HR"""
    application.add_handler(CallbackQueryHandler(view_approved_vacations, pattern="view_approved_vacations"))
