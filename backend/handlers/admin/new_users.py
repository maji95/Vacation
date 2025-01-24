from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, RegistrationQueue
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
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

        # Добавляем кнопки для управления очередью
        keyboard = [
            [InlineKeyboardButton("Одобрить всех", callback_data="approve_all")],
            [InlineKeyboardButton("« Назад", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in new_users: {e}")
        await query.edit_message_text("Произошла ошибка при получении списка новых пользователей.")
    finally:
        session.close()
        logger.info("new_users function completed")

async def approve_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Одобряет всех пользователей из очереди регистрации"""
    logger.info("Executing approve_all function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Получаем всех пользователей из очереди
        queue_users = session.query(RegistrationQueue).all()
        
        if not queue_users:
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "В очереди нет пользователей для одобрения.",
                reply_markup=reply_markup
            )
            return

        # Добавляем пользователей в основную таблицу
        for queue_user in queue_users:
            new_user = User(
                telegram_id=queue_user.telegram_id,
                full_name=queue_user.entered_name,
                vacation_days=0,
                is_admin=False
            )
            session.add(new_user)
            session.delete(queue_user)

        session.commit()

        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Все пользователи ({len(queue_users)}) были успешно добавлены.",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in approve_all: {e}")
        session.rollback()
        await query.edit_message_text("Произошла ошибка при одобрении пользователей.")
    finally:
        session.close()
        logger.info("approve_all function completed")
