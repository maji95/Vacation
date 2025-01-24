import logging
import os
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers.register import register_handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота"""
    try:
        # Создаем экземпляр приложения
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Регистрируем все обработчики
        register_handlers(application)
        
        logger.info("Бот запущен и готов к работе")
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()
