from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from config import get_session
from models import User, Role, Department, RegistrationQueue
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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
                logger.info(f"Новый пользователь {username} (ID: {user_id}) добавлен в очередь регистрации")
            else:
                logger.info(f"Пользователь {username} (ID: {user_id}) уже в очереди регистрации")
            return
        finally:
            session.close()
    
    # Формируем сообщение с информацией
    message = f"👤 Информация о пользователе:\n"
    message += f"Роль: {permissions['role'] or 'Не назначена'}\n"
    message += f"Отдел: {permissions['department'] or 'Не назначен'}\n"
    message += f"Дней отпуска: {permissions['vacation_days']}\n"
    message += f"Админ: {'Да' if permissions['is_admin'] else 'Нет'}\n\n"
    message += "Доступные действия:"
    
    # Создаем клавиатуру на основе прав доступа
    keyboard = [
        [InlineKeyboardButton("Запрос отпуска", callback_data="vacation_request")]
    ]

    if permissions["role"] in ["HR", "Department Head"]:
        keyboard.append([InlineKeyboardButton("Управление отпусками", callback_data="vacation_management")])
    
    if permissions["is_admin"]:
        keyboard.append([InlineKeyboardButton("Панель администратора", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню с доступными действиями"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.full_name
    logger.info(f"Пользователь {username} (ID: {user_id}) вернулся в главное меню")
    
    await query.answer()
    permissions = await get_user_permissions(user_id)
    
    # Формируем сообщение с информацией
    message = f"👤 Информация о пользователе:\n"
    message += f"Роль: {permissions['role'] or 'Не назначена'}\n"
    message += f"Отдел: {permissions['department'] or 'Не назначен'}\n"
    message += f"Дней отпуска: {permissions['vacation_days']}\n"
    message += f"Админ: {'Да' if permissions['is_admin'] else 'Нет'}\n\n"
    message += "Доступные действия:"
    
    # Создаем клавиатуру на основе прав доступа
    keyboard = [
        [InlineKeyboardButton("Запрос отпуска", callback_data="vacation_request")]
    ]

    if permissions["role"] in ["HR", "Department Head"]:
        keyboard.append([InlineKeyboardButton("Управление отпусками", callback_data="vacation_management")])
    
    if permissions["is_admin"]:
        keyboard.append([InlineKeyboardButton("Панель администратора", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup)

async def get_user_permissions(user_id: int) -> dict:
    """Проверяет права пользователя и возвращает словарь с информацией о правах доступа"""
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            return {
                "exists": False,
                "is_admin": False,
                "role": None,
                "department": None,
                "vacation_days": 0
            }
        
        role = session.query(Role).filter_by(id=user.role_id).first() if user.role_id else None
        department = session.query(Department).filter_by(id=user.department_id).first() if user.department_id else None
        
        if user.full_name:
            logger.info(f"Зарегистрированный пользователь {user.full_name} (ID: {user_id}) проверка прав доступа")
        
        return {
            "exists": True,
            "is_admin": user.is_admin,
            "role": role.name if role else None,
            "department": department.name if department else None,
            "vacation_days": user.vacation_days,
            "user": user
        }
    finally:
        session.close()

def register(application):
    """Регистрация обработчиков для role_check"""
    application.add_handler(CommandHandler("start", check_role))
