from telegram.ext import CallbackQueryHandler

from .vacation_approval import approve_direct_vacation, reject_direct_vacation

def register(application):
    """Регистрация обработчиков для директора"""
    # Управление отпусками непосредственных подчиненных
    application.add_handler(CallbackQueryHandler(approve_direct_vacation, pattern="approve_direct_vacation"))
    application.add_handler(CallbackQueryHandler(reject_direct_vacation, pattern="reject_direct_vacation"))
