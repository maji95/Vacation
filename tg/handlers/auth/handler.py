from ..core.base_handler import BaseRequestHandler
from ..core.request_types import RequestType
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User
from ..admin.system_monitor import SystemMonitor
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class AuthHandler(BaseRequestHandler):
    """Обработчик запросов на аутентификацию"""
    
    def __init__(self, request_type: RequestType):
        super().__init__(request_type)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Начинает процесс аутентификации"""
        if update.message:
            user_id = update.message.from_user.id
            await update.message.reply_text(
                "Добро пожаловать! Для использования бота необходимо пройти аутентификацию.\n"
                "Пожалуйста, введите ваш email в корпоративном домене:"
            )
        else:
            query = update.callback_query
            await query.answer()
            user_id = query.from_user.id
            await query.edit_message_text(
                "Добро пожаловать! Для использования бота необходимо пройти аутентификацию.\n"
                "Пожалуйста, введите ваш email в корпоративном домене:"
            )
            
        context.user_data['auth_state'] = 'waiting_email'
        
        # Логируем начало аутентификации
        await SystemMonitor.log_action(
            context,
            "auth_start",
            user_id,
            "Начат процесс аутентификации пользователя"
        )
    
    async def process(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Обрабатывает ввод данных для аутентификации"""
        # Эта функция будет вызываться для обработки текстовых сообщений
        # в процессе аутентификации, например, когда пользователь вводит email
        
        if 'auth_state' not in context.user_data:
            await update.message.reply_text(
                "Пожалуйста, начните процесс аутентификации с команды /start"
            )
            return
            
        auth_state = context.user_data.get('auth_state')
        
        if auth_state == 'waiting_email':
            email = update.message.text.strip().lower()
            
            # Проверяем формат email
            if not self._validate_email(email):
                await update.message.reply_text(
                    "Некорректный формат email. Пожалуйста, введите email в корпоративном домене:"
                )
                return
                
            # Проверяем, существует ли пользователь с таким email
            user = self.session.query(User).filter_by(email=email).first()
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
        
        elif auth_state == 'waiting_password':
            password = update.message.text
            email = context.user_data.get('email')
            
            # Проверяем пароль
            user = self.session.query(User).filter_by(email=email).first()
            if not user or not self._verify_password(user, password):
                await update.message.reply_text(
                    "Неверный пароль. Пожалуйста, попробуйте снова:"
                )
                return
                
            # Аутентификация успешна
            user.telegram_id = update.message.from_user.id
            self.session.commit()
            
            # Логируем успешную аутентификацию
            await SystemMonitor.log_action(
                context,
                "auth_success",
                user.telegram_id,
                f"Пользователь {user.full_name} успешно прошел аутентификацию"
            )
            
            # Очищаем данные аутентификации
            context.user_data.clear()
            
            # Показываем главное меню
            from ..menu import show_menu
            await show_menu(update, context)
    
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Подтверждает аутентификацию"""
        # Этот метод может использоваться для подтверждения аутентификации
        # через внешние системы или для двухфакторной аутентификации
        pass
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Отменяет процесс аутентификации"""
        if update.message:
            await update.message.reply_text(
                "Процесс аутентификации отменен. Для начала работы с ботом введите /start"
            )
        else:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                "Процесс аутентификации отменен. Для начала работы с ботом введите /start"
            )
            
        # Очищаем данные аутентификации
        context.user_data.clear()
    
    def _validate_email(self, email: str) -> bool:
        """Проверяет формат email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _verify_password(self, user: User, password: str) -> bool:
        """Проверяет пароль пользователя"""
        # В реальной системе здесь должна быть безопасная проверка пароля
        # Например, с использованием хеширования
        return user.password == password
