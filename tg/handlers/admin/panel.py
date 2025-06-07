from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, RegistrationQueue
import logging

logger = logging.getLogger(__name__)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отображает административную панель."""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or not user.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        new_users_count = session.query(RegistrationQueue).count()

        message = (
            "🔧 Панель администратора\n\n"
            f"📝 Новых заявок на регистрацию: {new_users_count}\n\n"
            "Выберите раздел для управления:"
        )

        keyboard = [
            [InlineKeyboardButton("Просмотреть заявки", callback_data="new_users")],
            [InlineKeyboardButton("Управление пользователями", callback_data="admin_users")],
            [InlineKeyboardButton("Статистика запросов", callback_data="admin_stats")],
            [InlineKeyboardButton("Настройки системы", callback_data="admin_settings")],
            [InlineKeyboardButton("« Назад", callback_data="show_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при загрузке админ-панели: {e}")
        await query.edit_message_text(
            "Произошла ошибка при загрузке панели администратора."
        )
    finally:
        session.close()


async def process_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команды админ-панели."""
    query = update.callback_query
    await query.answer()

    command = query.data

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or not user.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        if command == "admin_users":
            await show_users_management(update, context)
        elif command == "admin_stats":
            await show_stats(update, context)
        elif command == "admin_settings":
            await show_settings(update, context)
        else:
            await query.edit_message_text(
                "Неизвестная команда. Пожалуйста, вернитесь в меню администратора.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
                ),
            )
    except Exception as e:
        logger.error(f"Error in process_admin_command: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()


async def show_users_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню управления пользователями."""
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("Добавить пользователя", callback_data="admin_add_user")],
        [InlineKeyboardButton("Список пользователей", callback_data="admin_list_users")],
        [InlineKeyboardButton("« Назад", callback_data="admin_panel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "👥 Управление пользователями\n\n",
        "Выберите действие:",
        reply_markup=reply_markup,
    )


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику запросов."""
    query = update.callback_query

    keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📊 Статистика запросов\n\n",
        "Здесь будет отображаться статистика запросов.",
        reply_markup=reply_markup,
    )


async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает настройки системы."""
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("Настройки утверждения", callback_data="admin_approval_settings")],
        [InlineKeyboardButton("Настройки уведомлений", callback_data="admin_notification_settings")],
        [InlineKeyboardButton("« Назад", callback_data="admin_panel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "⚙️ Настройки системы\n\n",
        "Выберите категорию настроек:",
        reply_markup=reply_markup,
    )
