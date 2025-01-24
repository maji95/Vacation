from telegram.ext import CallbackQueryHandler

from .vacation_approval import approve_team_vacation, reject_team_vacation

def register(application):
    """Регистрация обработчиков для начальника отдела"""
    # Управление отпусками команды
    application.add_handler(CallbackQueryHandler(approve_team_vacation, pattern="approve_team_vacation"))
    application.add_handler(CallbackQueryHandler(reject_team_vacation, pattern="reject_team_vacation"))
