from telegram.ext import CallbackQueryHandler

from .employee_management import manage_employees, add_employee, edit_employee, delete_employee
from .vacation_approval import approve_vacation_request, reject_vacation_request
from .reports import hr_reports

def register(application):
    """Регистрация обработчиков для HR"""
    # Управление сотрудниками
    application.add_handler(CallbackQueryHandler(manage_employees, pattern="manage_employees"))
    application.add_handler(CallbackQueryHandler(add_employee, pattern="add_employee"))
    application.add_handler(CallbackQueryHandler(edit_employee, pattern="edit_employee"))
    application.add_handler(CallbackQueryHandler(delete_employee, pattern="delete_employee"))
    
    # Управление отпусками
    application.add_handler(CallbackQueryHandler(approve_vacation_request, pattern="hr_approve_vacation"))
    application.add_handler(CallbackQueryHandler(reject_vacation_request, pattern="hr_reject_vacation"))
    
    # Отчеты HR
    application.add_handler(CallbackQueryHandler(hr_reports, pattern="hr_reports"))
