import logging
import os
from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN
from handlers import inline, role_check

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    """Обработчик команды /start"""
    await role_check.check_role(update, context)

def main():
    """Основная функция запуска бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()

        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        
        # Регистрируем inline обработчики
        inline.register(application)

        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()
