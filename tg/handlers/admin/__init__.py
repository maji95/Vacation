from telegram.ext import CallbackQueryHandler

from .panel import admin_panel
from .new_users import new_users, approve_all

def register(application):
    """Регистрация обработчиков админ-панели"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    application.add_handler(CallbackQueryHandler(new_users, pattern="new_users"))
    application.add_handler(CallbackQueryHandler(approve_all, pattern="approve_all"))
