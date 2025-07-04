from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, Department, RegistrationQueue
import logging

logger = logging.getLogger(__name__)

async def check_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверяет роль пользователя и показывает соответствующую информацию"""
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.full_name
    logger.info(f"Пользователь {username} (ID: {user_id}) использовал команду /start")
    
    permissions = await get_user_permissions(user_id)
    
    if not permissions["exists"]:
        # Если пользователь не найден, добавляем его в очередь регистрации
        session = get_session()
        try:
            queue_user = session.query(RegistrationQueue).filter_by(telegram_id=user_id).first()
            if not queue_user:
                new_queue_user = RegistrationQueue(
                    telegram_id=user_id,
                    entered_name=update.message.from_user.full_name
                )
                session.add(new_queue_user)
                session.commit()
                logger.info(f"Пользователь {username} (ID: {user_id}) добавлен в очередь регистрации")
            await update.message.reply_text(
                "Вы не зарегистрированы в системе. Ваша заявка отправлена на рассмотрение администратору."
            )
            return
        finally:
            session.close()

    # Показываем меню в зависимости от роли
    keyboard = [
        [InlineKeyboardButton("Запрос отпуска", callback_data="vacation_request")]
    ]

    # Кнопки для администратора
    if permissions["is_admin"]:
        keyboard.append([InlineKeyboardButton("Админ-панель", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Добро пожаловать, {permissions['user'].full_name}!", 
        reply_markup=reply_markup
    )

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню с доступными действиями"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    permissions = await get_user_permissions(user_id)
    
    if not permissions["exists"]:
        await query.edit_message_text(
            "Вы не зарегистрированы в системе. Ваша заявка отправлена на рассмотрение администратору."
        )
        return

    # Основные кнопки
    keyboard = [
        [InlineKeyboardButton("Запрос отпуска", callback_data="vacation_request")]
    ]

    # Кнопки для администратора
    if permissions["is_admin"]:
        keyboard.append([InlineKeyboardButton("Админ-панель", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"Добро пожаловать, {permissions['user'].full_name}!", 
        reply_markup=reply_markup
    )

async def get_user_permissions(user_id: int):
    """Проверяет права пользователя и возвращает словарь с информацией о правах доступа"""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        
        if not user:
            return {
                "exists": False,
                "is_admin": False,
                "department": None,
                "vacation_days": 0,
                "user": None
            }
        
        department = session.query(Department).filter_by(id=user.department_id).first() if user.department_id else None
        
        if user.full_name:
            logger.info(f"Зарегистрированный пользователь {user.full_name} (ID: {user_id}) проверка прав доступа")
        
        return {
            "exists": True,
            "is_admin": user.is_admin,
            "department": department.name if department else None,
            "vacation_days": user.vacation_days,
            "user": user
        }
    finally:
        session.close()
