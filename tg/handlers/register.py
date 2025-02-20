from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .auth import register_handlers as register_auth
from .admin import register_handlers as register_admin
from .vacation import register_handlers as register_vacation
from .approval import create_approval_request, send_approval_request, view_pending_requests, handle_approval
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
    
    # Регистрируем обработчики утверждения
    application.add_handler(CallbackQueryHandler(view_pending_requests, pattern="^view_pending_requests$"))
    application.add_handler(CallbackQueryHandler(
        lambda update, context: handle_approval(
            update,
            context,
            int(update.callback_query.data.split('_')[-1]),
            update.callback_query.data.split('_')[1],
            True
        ),
        pattern=r"^approve_(first|second|final)_\d+$"
    ))
    application.add_handler(CallbackQueryHandler(
        lambda update, context: handle_approval(
            update,
            context,
            int(update.callback_query.data.split('_')[-1]),
            update.callback_query.data.split('_')[1],
            False
        ),
        pattern=r"^reject_(first|second|final)_\d+$"
    ))
