from telegram.ext import Application, CallbackQueryHandler
from .vacation_approval import handle_vacation_approval, approve_vacation, reject_vacation
from .view_requests import view_requests

def register_handlers(application: Application):
    """Регистрация обработчиков для директора"""
    application.add_handler(CallbackQueryHandler(view_requests, pattern="view_vacation_requests"))
    application.add_handler(CallbackQueryHandler(approve_vacation, pattern="approve_vacation_\\d+"))
    application.add_handler(CallbackQueryHandler(reject_vacation, pattern="reject_vacation_\\d+"))
