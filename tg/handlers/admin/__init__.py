from telegram.ext import Application, CallbackQueryHandler
from .panel import admin_panel
from .new_users import new_users
from .system_monitor import SystemMonitor
from .admin import admin_panel, process_admin_command
from .handler import AdminHandler

__all__ = ['admin_panel', 'new_users', 'SystemMonitor', 'process_admin_command', 'AdminHandler']

def register_handlers(application: Application):
    """Регистрация обработчиков админ-панели"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    application.add_handler(CallbackQueryHandler(new_users, pattern="new_users"))
