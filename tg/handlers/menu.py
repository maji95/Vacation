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
    query = update.callback_query
    if query:
        await query.answer()
    
    session = get_session()
    try:
        # Получаем пользователя
        user = session.query(User).filter_by(
            telegram_id=query.from_user.id if query else update.message.from_user.id
        ).first()
        
        if not user:
            text = "Пользователь не найден. Пожалуйста, зарегистрируйтесь."
            keyboard = [[InlineKeyboardButton("Регистрация", callback_data="register")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            # Формируем основное меню
            keyboard = []
            
            # Кнопка запроса отпуска
            keyboard.append([InlineKeyboardButton("📅 Запрос отпуска", callback_data="vacation_request")])
            
            # Добавляем кнопки в зависимости от роли пользователя
            if user.is_director:
                keyboard.append([InlineKeyboardButton("👀 Просмотр заявок", callback_data="view_pending_requests")])
            
            if user.is_admin:
                keyboard.append([InlineKeyboardButton("⚙️ Админ панель", callback_data="admin_panel")])
            
            text = f"Добро пожаловать, {user.full_name}!\nВыберите действие:"
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем или редактируем сообщение
        if query:
            await query.edit_message_text(text=text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text=text, reply_markup=reply_markup)
            
    except Exception as e:
        logger.error(f"Error in show_menu: {e}")
        error_text = "Произошла ошибка при отображении меню."
        if query:
            await query.edit_message_text(text=error_text)
        else:
            await update.message.reply_text(text=error_text)
    finally:
        session.close()
