from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from config import get_session
from models import User
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логирование информации о пользователе
    user = update.effective_user
    logger.info(f"Пользователь {user.full_name} (@{user.username}) запустил бота. ID: {user.id}")

    chat_id = update.effective_chat.id
    session = get_session()
    session.rollback()  # Сброс транзакции на случай ошибок
    users = session.query(User).all()  # Получаем всех пользователей

    if users:
        user_list = "\n".join([f"{user.id}. {user.full_name} — {user.vacation_days} дней отпуска" for user in users])
        message = f"Вот список пользователей:\n{user_list}"
    else:
        message = "В базе данных пока нет пользователей."

    await context.bot.send_message(chat_id=chat_id, text=message)

def register(application):
    application.add_handler(CommandHandler("start", start))
