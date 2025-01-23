from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers import start_handler

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    start_handler.register(application)

    # Запуск бота
    print("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
