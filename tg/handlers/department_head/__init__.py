from telegram.ext import Application, CallbackQueryHandler
from .vacation_approval import approve_team_vacation, reject_team_vacation

def register_handlers(application: Application):
    """Регистрация обработчиков начальника отдела"""
    application.add_handler(CallbackQueryHandler(approve_team_vacation, pattern="approve_team_vacation"))
    application.add_handler(CallbackQueryHandler(reject_team_vacation, pattern="reject_team_vacation"))
