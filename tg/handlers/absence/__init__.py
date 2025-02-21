from telegram.ext import Application, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from .request import (
    absence_request,
    handle_date,
    handle_start_time,
    handle_end_time,
    cancel_absence,
    confirm_absence,
    WAITING_DATE,
    WAITING_START_TIME,
    WAITING_END_TIME,
    WAITING_CONFIRMATION
)
import logging

logger = logging.getLogger(__name__)

def register_handlers(application: Application):
    """Регистрация обработчиков отсутствия"""
    logger.info("Регистрируем обработчики отсутствия")
    
    # Создаем ConversationHandler для запроса отсутствия
    absence_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(absence_request, pattern="^absence_request$")],
        states={
            WAITING_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)],
            WAITING_START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_start_time)],
            WAITING_END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_end_time)],
            WAITING_CONFIRMATION: [
                CallbackQueryHandler(confirm_absence, pattern="^confirm_absence$"),
                CallbackQueryHandler(cancel_absence, pattern="^cancel_absence$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(cancel_absence, pattern="^cancel_absence$"),
            CallbackQueryHandler(confirm_absence, pattern="^confirm_absence$")
        ]
    )
    
    # Регистрируем ConversationHandler
    application.add_handler(absence_conv_handler)
    
    logger.info("Обработчики отсутствия зарегистрированы")
