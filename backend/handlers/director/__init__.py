from telegram.ext import CallbackQueryHandler

from .department_management import manage_departments, add_department, edit_department, delete_department
from .reports import view_reports, generate_report
from .statistics import view_statistics

def register(application):
    """Регистрация обработчиков для директора"""
    # Управление отделами
    application.add_handler(CallbackQueryHandler(manage_departments, pattern="manage_departments"))
    application.add_handler(CallbackQueryHandler(add_department, pattern="add_department"))
    application.add_handler(CallbackQueryHandler(edit_department, pattern="edit_department"))
    application.add_handler(CallbackQueryHandler(delete_department, pattern="delete_department"))
    
    # Отчеты и статистика
    application.add_handler(CallbackQueryHandler(view_reports, pattern="view_reports"))
    application.add_handler(CallbackQueryHandler(generate_report, pattern="generate_report"))
    application.add_handler(CallbackQueryHandler(view_statistics, pattern="view_statistics"))
