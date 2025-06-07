import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from .menu import show_menu
from .approval import view_pending_requests, approve_request, reject_request
from .core.request_types import RequestType
from .core.dispatcher import RequestDispatcher

# Настройка логирования
logger = logging.getLogger(__name__)

def register_handlers(application: Application):
    """Регистрация всех обработчиков приложения"""
    logger.info("Начало регистрации обработчиков")
    
    # Регистрируем команду /start и callback для меню
    application.add_handler(CommandHandler("start", show_menu))
    application.add_handler(CallbackQueryHandler(show_menu, pattern="^show_menu$"))
    
    # Регистрируем обработчики для отпусков через диспетчер
    application.add_handler(CallbackQueryHandler(
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.VACATION, "start"
        ),
        pattern="^vacation_request$"
    ))
    
    application.add_handler(CallbackQueryHandler(
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.VACATION, "process"
        ),
        pattern="^vacation_by_days$"
    ))
    
    application.add_handler(CallbackQueryHandler(
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.VACATION, "confirm"
        ),
        pattern="^confirm_vacation$"
    ))
    
    application.add_handler(CallbackQueryHandler(
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.VACATION, "cancel"
        ),
        pattern="^restart_vacation_request$"
    ))
    
    # Регистрируем обработчики для админ-панели через диспетчер
    application.add_handler(CallbackQueryHandler(
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.ADMIN, "start"
        ),
        pattern="^admin_menu$"
    ))
    
    application.add_handler(CallbackQueryHandler(
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.ADMIN, "process"
        ),
        pattern="^admin_"
    ))
    
    # Обработчики для утверждения запросов
    application.add_handler(CallbackQueryHandler(view_pending_requests, pattern="^view_pending_requests$"))
    application.add_handler(CallbackQueryHandler(approve_request, pattern="^approve_"))
    application.add_handler(CallbackQueryHandler(reject_request, pattern="^reject_"))
    
    # Обработчики для аутентификации
    application.add_handler(CommandHandler("auth", 
        lambda update, context: RequestDispatcher.dispatch_request(
            update, context, RequestType.AUTH, "start"
        )
    ))
    
    # Обработчик для текстовых сообщений (для ввода дат и т.д.)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))
    
    logger.info("Регистрация обработчиков завершена")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений в зависимости от состояния пользователя"""
    user_data = context.user_data
    
    # Определяем, какой тип запроса обрабатывается
    if 'vacation_state' in user_data:
        # Обработка сообщений для запросов на отпуск
        from .vacation.request import process_vacation_message
        await process_vacation_message(update, context)
    elif 'auth_state' in user_data:
        # Обработка сообщений для аутентификации
        await RequestDispatcher.dispatch_request(
            update, context, RequestType.AUTH, "process"
        )
    elif 'admin_state' in user_data:
        # Обработка сообщений для админ-панели
        await RequestDispatcher.dispatch_request(
            update, context, RequestType.ADMIN, "process"
        )
    else:
        # Если состояние не определено, отправляем инструкцию
        await update.message.reply_text(
            "Я не понимаю, что вы хотите сделать. Пожалуйста, используйте команду /start для доступа к меню."
        )
