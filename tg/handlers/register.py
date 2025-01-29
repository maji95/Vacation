from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .auth import register_handlers as register_auth
from .admin import register_handlers as register_admin
from .vacation import register_handlers as register_vacation
from .director import register_handlers as register_director
from .hr import register_handlers as register_hr
from .department_head import register_handlers as register_department_head
from .menu import show_menu

def register_handlers(application: Application):
    """Регистрация всех обработчиков приложения"""
    # Регистрируем команду /start и callback для меню
    application.add_handler(CommandHandler("start", show_menu))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="show_menu"))
    
    # Регистрируем обработчики аутентификации
    register_auth(application)
    
    # Регистрируем обработчики отпуска
    register_vacation(application)
    
    # Регистрируем обработчики админ-панели
    register_admin(application)
    
    # Регистрируем обработчики для разных ролей
    register_director(application)
    register_hr(application)
    register_department_head(application)
