from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

async def start_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс аутентификации"""
    if update.message:
        await update.message.reply_text(
            "Добро пожаловать! Для использования бота необходимо пройти аутентификацию.\n"
            "Пожалуйста, введите ваш email в корпоративном домене:"
        )
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Добро пожаловать! Для использования бота необходимо пройти аутентификацию.\n"
            "Пожалуйста, введите ваш email в корпоративном домене:"
        )
        
    context.user_data['auth_state'] = 'waiting_email'

async def process_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод данных для аутентификации"""
    if 'auth_state' not in context.user_data:
        await update.message.reply_text(
            "Пожалуйста, начните процесс аутентификации с команды /start"
        )
        return
        
    auth_state = context.user_data.get('auth_state')
    
    if auth_state == 'waiting_email':
        email = update.message.text.strip().lower()
        
        # Проверяем формат email
        if not validate_email(email):
            await update.message.reply_text(
                "Некорректный формат email. Пожалуйста, введите email в корпоративном домене:"
            )
            return
            
        # Проверяем, существует ли пользователь с таким email
        session = get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                await update.message.reply_text(
                    "Пользователь с таким email не найден. Пожалуйста, проверьте правильность ввода или обратитесь к администратору."
                )
                return
                
            # Сохраняем email и переходим к вводу пароля
            context.user_data['email'] = email
            context.user_data['auth_state'] = 'waiting_password'
            
            await update.message.reply_text(
                "Теперь введите ваш пароль:"
            )
        finally:
            session.close()
    
    elif auth_state == 'waiting_password':
        password = update.message.text
        email = context.user_data.get('email')
        
        # Проверяем пароль
        session = get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if not user or not verify_password(user, password):
                await update.message.reply_text(
                    "Неверный пароль. Пожалуйста, попробуйте снова:"
                )
                return
                
            # Аутентификация успешна
            user.telegram_id = update.message.from_user.id
            session.commit()
            
            # Очищаем данные аутентификации
            context.user_data.clear()
            
            # Показываем главное меню
            from ..menu import show_menu
            await show_menu(update, context)
        finally:
            session.close()

def validate_email(email: str) -> bool:
    """Проверяет формат email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def verify_password(user: User, password: str) -> bool:
    """Проверяет пароль пользователя"""
    # В реальной системе здесь должна быть безопасная проверка пароля
    # Например, с использованием хеширования
    return user.password == password
