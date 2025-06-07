from telegram.ext import CallbackQueryHandler
from .request import (
    vacation_request,
    vacation_by_days,
    confirm_vacation,
    restart_vacation_request
)
import logging

logger = logging.getLogger(__name__)


def register_handlers(application):
    """Регистрация обработчиков для отпусков"""
    logger.info("Регистрируем обработчики отпуска")
    
    # Основные обработчики
    application.add_handler(CallbackQueryHandler(vacation_request, pattern="vacation_request"))
    application.add_handler(CallbackQueryHandler(vacation_by_days, pattern="vacation_by_days"))
    application.add_handler(CallbackQueryHandler(confirm_vacation, pattern="confirm_vacation"))
    application.add_handler(CallbackQueryHandler(restart_vacation_request, pattern="restart_vacation_request"))

    logger.info("Обработчики отпуска зарегистрированы")
