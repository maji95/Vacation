from telegram.ext import CallbackQueryHandler

from .vacation_approval import view_approved_vacations

def register(application):
    """Регистрация обработчиков для HR"""
    # Просмотр утвержденных отпусков
    application.add_handler(CallbackQueryHandler(view_approved_vacations, pattern="view_approved_vacations"))
