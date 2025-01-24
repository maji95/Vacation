from telegram.ext import CommandHandler, CallbackQueryHandler

def register_handlers(application):
    """Регистрация всех обработчиков приложения"""
    from .role_check import check_role, show_menu
    from .admin import register as register_admin
    from .vacation import register as register_vacation
    from .director import register as register_director
    from .hr import register as register_hr
    from .department_head import register as register_department_head
    
    # Регистрируем основные команды
    application.add_handler(CommandHandler("start", check_role))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="show_menu"))
    
    # Регистрируем обработчики отпуска
    register_vacation(application)
    
    # Регистрируем обработчики админ-панели
    register_admin(application)
    
    # Регистрируем обработчики для разных ролей
    register_director(application)
    register_hr(application)
    register_department_head(application)
