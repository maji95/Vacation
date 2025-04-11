from telegram import Update
from telegram.ext import ContextTypes
from .request_types import RequestType
import importlib
import logging

logger = logging.getLogger(__name__)

class RequestDispatcher:
    """Центральный диспетчер для маршрутизации запросов"""
    
    @staticmethod
    async def dispatch_request(update: Update, context: ContextTypes.DEFAULT_TYPE, request_type: RequestType, action: str, **kwargs):
        """
        Направляет запрос в соответствующий модуль обработки
        
        Args:
            update: Объект Update от Telegram
            context: Контекст от Telegram
            request_type: Тип запроса (из RequestType)
            action: Конкретное действие в рамках типа запроса
            **kwargs: Дополнительные параметры для обработчика
        """
        try:
            # Определяем модуль для обработки
            module_name = request_type.handler_module
            
            # Динамически импортируем модуль
            module_path = f"handlers.{module_name}.handler"
            handler_module = importlib.import_module(module_path)
            
            # Получаем класс обработчика
            handler_class = getattr(handler_module, f"{module_name.capitalize()}Handler")
            
            # Создаем экземпляр обработчика
            handler = handler_class(request_type)
            
            # Вызываем соответствующий метод
            if hasattr(handler, action):
                method = getattr(handler, action)
                await method(update, context, **kwargs)
            else:
                logger.error(f"Action {action} not found in handler {handler_class.__name__}")
                if update.callback_query:
                    await update.callback_query.edit_message_text("Извините, запрошенное действие недоступно.")
                else:
                    await update.message.reply_text("Извините, запрошенное действие недоступно.")
                
        except ImportError as e:
            logger.error(f"Error importing module for request type {request_type}: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text("Извините, произошла ошибка при обработке вашего запроса.")
            else:
                await update.message.reply_text("Извините, произошла ошибка при обработке вашего запроса.")
        except Exception as e:
            logger.error(f"Error dispatching request: {e}")
            if update.callback_query:
                await update.callback_query.edit_message_text("Извините, произошла ошибка при обработке вашего запроса.")
            else:
                await update.message.reply_text("Извините, произошла ошибка при обработке вашего запроса.")
