from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from .auth import register_handlers as register_auth
from .admin import register_handlers as register_admin
from .vacation import register_handlers as register_vacation
from .absence import register_handlers as register_absence
from .approval import create_approval_request, send_approval_request, view_pending_requests, handle_approval
from .approval.create_hours_request import handle_hours_approval
from .menu import show_menu
import logging

logger = logging.getLogger(__name__)

def register_handlers(application: Application):
    """Регистрация всех обработчиков приложения"""
    logger.info("Начало регистрации обработчиков")
    
    # Регистрируем команду /start и callback для меню
    application.add_handler(CommandHandler("start", show_menu))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="show_menu"))
    
    # Регистрируем обработчики утверждения
    application.add_handler(CallbackQueryHandler(view_pending_requests, pattern="^view_pending_requests$"))
    
    # Обработчики утверждения отпусков
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
    
    # Обработчики утверждения отсутствий
    application.add_handler(CallbackQueryHandler(
        lambda update, context: handle_hours_approval(
            update,
            context,
            int(update.callback_query.data.split('_')[-1]),
            update.callback_query.data.split('_')[2],
            True
        ),
        pattern=r"^approve_absence_(first|second|final)_\d+$"
    ))
    application.add_handler(CallbackQueryHandler(
        lambda update, context: handle_hours_approval(
            update,
            context,
            int(update.callback_query.data.split('_')[-1]),
            update.callback_query.data.split('_')[2],
            False
        ),
        pattern=r"^reject_absence_(first|second|final)_\d+$"
    ))
    
    # Регистрируем обработчики отсутствия
    register_absence(application)
    
    # Регистрируем обработчики отпуска
    register_vacation(application)
    
    # Регистрируем обработчики аутентификации
    register_auth(application)
    
    # Регистрируем обработчики админ-панели
    register_admin(application)
    
    logger.info("Все обработчики зарегистрированы")
