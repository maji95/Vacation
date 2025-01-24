from telegram.ext import CallbackQueryHandler

from .panel import admin_panel
from .users_list import list_users
from .new_users import new_users, approve_all
from .add_user import add_user
from .delete_users import delete_users

def register(application):
    """Регистрация всех обработчиков админ-панели"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    application.add_handler(CallbackQueryHandler(new_users, pattern="new_users"))
    application.add_handler(CallbackQueryHandler(list_users, pattern="list_users"))
    application.add_handler(CallbackQueryHandler(add_user, pattern="add_user"))
    application.add_handler(CallbackQueryHandler(delete_users, pattern="delete_users"))
    application.add_handler(CallbackQueryHandler(approve_all, pattern="approve_all"))
