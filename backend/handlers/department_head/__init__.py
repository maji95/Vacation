from telegram.ext import CallbackQueryHandler

from .team_management import manage_team, view_team_schedule
from .vacation_approval import approve_team_vacation, reject_team_vacation
from .reports import department_reports

def register(application):
    """Регистрация обработчиков для начальника отдела"""
    # Управление командой
    application.add_handler(CallbackQueryHandler(manage_team, pattern="manage_team"))
    application.add_handler(CallbackQueryHandler(view_team_schedule, pattern="team_schedule"))
    
    # Управление отпусками команды
    application.add_handler(CallbackQueryHandler(approve_team_vacation, pattern="approve_team_vacation"))
    application.add_handler(CallbackQueryHandler(reject_team_vacation, pattern="reject_team_vacation"))
    
    # Отчеты отдела
    application.add_handler(CallbackQueryHandler(department_reports, pattern="department_reports"))
