from telegram import Update
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений для отпусков"""
    logger.info("Executing handle_message function")
    
    # Проверяем, находится ли пользователь в процессе запроса отпуска
    vacation_state = context.user_data.get('vacation_state')
    if not vacation_state:
        return

    session = get_session()
    try:
        # Получаем информацию о пользователе
        user = session.query(User).filter_by(telegram_id=update.message.from_user.id).first()
        if not user:
            await update.message.reply_text("Пользователь не найден.")
            return

        if vacation_state == 'waiting_days':
            # Обработка запроса отпуска по дням
            try:
                # Здесь будет логика обработки дат
                await update.message.reply_text(
                    "Ваш запрос на отпуск принят и отправлен на рассмотрение."
                )
            except ValueError as e:
                await update.message.reply_text(
                    "Неверный формат дат. Используйте формат ДД.ММ.ГГГГ - ДД.ММ.ГГГГ"
                )
            finally:
                # Очищаем состояние
                context.user_data.pop('vacation_state', None)

        elif vacation_state == 'waiting_hours':
            # Обработка запроса отпуска по часам
            try:
                # Здесь будет логика обработки часов
                await update.message.reply_text(
                    "Ваш запрос на отпуск по часам принят и отправлен на рассмотрение."
                )
            except ValueError as e:
                await update.message.reply_text(
                    "Неверный формат. Используйте формат ДД.ММ.ГГГГ 4"
                )
            finally:
                # Очищаем состояние
                context.user_data.pop('vacation_state', None)

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()
        logger.info("handle_message function completed")
