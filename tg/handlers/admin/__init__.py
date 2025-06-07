from telegram.ext import Application, CallbackQueryHandler
from .panel import admin_panel
from .new_users import new_users

def register_handlers(application: Application):
    """Регистрация обработчиков админ-панели"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    application.add_handler(CallbackQueryHandler(new_users, pattern="new_users"))
