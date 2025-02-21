from telegram.ext import ContextTypes
from config import get_session
from models import User
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Класс для мониторинга системных процессов"""
    
    @staticmethod
    async def log_action(
        context: ContextTypes.DEFAULT_TYPE,
        action_type: str,
        user_id: int,
        details: str
    ):
        """
        Логирует действие в системе и уведомляет администраторов
        
        :param context: Контекст телеграм бота
        :param action_type: Тип действия (vacation_request, approval, registration, etc.)
        :param user_id: ID пользователя, совершившего действие
        :param details: Детали действия
        """
        session = get_session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            user_name = user.full_name if user else f"Unknown User (ID: {user_id})"
            
            # Логируем действие
            log_message = f"ACTION: {action_type} | USER: {user_name} | DETAILS: {details}"
            logger.info(log_message)
            
            # Получаем список администраторов
            admins = session.query(User).filter_by(is_admin=True).all()
            
            # Формируем сообщение для админов
            admin_message = (
                f"🔔 Новое действие в системе\n\n"
                f"👤 Пользователь: {user_name}\n"
                f"📝 Действие: {action_type}\n"
                f"ℹ️ Детали: {details}\n"
                f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            )
            
            # Отправляем уведомление каждому админу
            for admin in admins:
                try:
                    await context.bot.send_message(
                        chat_id=admin.telegram_id,
                        text=admin_message
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin.full_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in log_action: {e}")
        finally:
            session.close()

# Экспортируем класс
__all__ = ['SystemMonitor']
