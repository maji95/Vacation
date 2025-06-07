from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .permissions import check_role, show_menu, get_user_permissions

def register_handlers(application: Application):
    """Регистрация обработчиков для аутентификации и авторизации"""
    application.add_handler(CommandHandler("start", check_role))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="show_menu"))

__all__ = ['register_handlers', 'check_role', 'show_menu', 'get_user_permissions']
