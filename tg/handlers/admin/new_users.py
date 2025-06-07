from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, RegistrationQueue
import logging

logger = logging.getLogger(__name__)

async def new_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список новых пользователей в очереди регистрации"""
    logger.info("Executing new_users function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Получаем всех пользователей из очереди регистрации
        queue_users = session.query(RegistrationQueue).all()

        if not queue_users:
            # Если очередь пуста
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "В очереди нет новых пользователей.",
                reply_markup=reply_markup
            )
            return

        # Формируем сообщение со списком пользователей
        message = "Пользователи в очереди регистрации:\n\n"
        for user in queue_users:
            message += f"👤 {user.entered_name}\n"
            message += f"   ID: {user.telegram_id}\n"
            message += f"   Дата запроса: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"

        # Добавляем кнопку возврата
        keyboard = [
            [InlineKeyboardButton("« Назад", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при загрузке списка новых пользователей: {e}")
        await query.edit_message_text("Произошла ошибка при загрузке списка пользователей.")
    finally:
        session.close()
        logger.info("new_users function completed")
