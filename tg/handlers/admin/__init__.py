from telegram.ext import Application, CallbackQueryHandler
from .panel import admin_panel, process_admin_command
from .new_users import new_users

def register_handlers(application: Application):
    """Регистрация обработчиков админ-панели"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    application.add_handler(
        CallbackQueryHandler(process_admin_command, pattern="^admin_(?!panel$).+")
    )
    application.add_handler(CallbackQueryHandler(new_users, pattern="new_users"))
