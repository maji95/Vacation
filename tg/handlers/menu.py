from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать главное меню"""
    # Определяем, откуда пришел запрос
    if update.message:
        message = update.message
    else:
        message = update.callback_query.message
        await update.callback_query.answer()

    session = get_session()
    try:
        # Получаем пользователя
        user = None
        if update.message:
            user = session.query(User).filter_by(telegram_id=update.message.from_user.id).first()
        else:
            user = session.query(User).filter_by(telegram_id=update.callback_query.from_user.id).first()

        if not user:
            keyboard = [[InlineKeyboardButton("🔑 Авторизация", callback_data="auth")]]
            if update.message:
                await message.reply_text(
                    "Добро пожаловать! Для начала работы необходимо авторизоваться.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await message.edit_text(
                    "Добро пожаловать! Для начала работы необходимо авторизоваться.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            return

        # Формируем клавиатуру в зависимости от прав пользователя
        keyboard = []
        
        # Добавляем кнопки для обычных пользователей
        if user.is_active:
            keyboard.append([InlineKeyboardButton("📅 Запрос отпуска", callback_data="vacation_request")])

        # Добавляем кнопки для HR и директоров
        if user.is_hr or user.is_director:
            keyboard.append([InlineKeyboardButton("📋 Просмотр заявок", callback_data="view_pending_requests")])

        # Добавляем кнопки для администраторов
        if user.is_admin or user.is_superuser:
            keyboard.append([InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin_panel")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем или редактируем сообщение
        menu_text = f"👋 Здравствуйте, {user.full_name}!\n"
        if user.vacation_days > 0:
            menu_text += f"\n💡 У вас доступно {int(user.vacation_days)} дней отпуска."
        
        if update.message:
            await message.reply_text(menu_text, reply_markup=reply_markup)
        else:
            await message.edit_text(menu_text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in show_menu: {e}")
        if update.message:
            await message.reply_text("Произошла ошибка при отображении меню.")
        else:
            await message.edit_text("Произошла ошибка при отображении меню.")
    finally:
        session.close()
