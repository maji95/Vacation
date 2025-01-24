from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, Role, Department
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список всех пользователей с их ролями и департаментами"""
    logger.info("Executing list_users function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права администратора
        admin = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not admin or not admin.is_admin:
            await query.edit_message_text("У вас нет прав администратора.")
            return

        # Получаем всех пользователей
        users = session.query(User).all()

        # Формируем сообщение со списком пользователей
        message = "Список пользователей:\n\n"
        for user in users:
            # Определяем роль пользователя
            role_name = "Не назначена"
            if user.role_id:
                role = session.query(Role).filter_by(id=user.role_id).first()
                if role:
                    role_name = role.name

            # Определяем отдел пользователя
            department_name = "Не назначен"
            if user.department_id:
                department = session.query(Department).filter_by(id=user.department_id).first()
                if department:
                    department_name = department.name

            # Формируем информацию о пользователе
            user_info = f"👤 Информация о пользователе:\n"
            user_info += f"Имя: {user.full_name}\n"
            user_info += f"Роль: {role_name}\n"
            user_info += f"Отдел: {department_name}\n"
            user_info += f"Дней отпуска: {user.vacation_days}\n"
            user_info += f"Админ: {'Да' if user.is_admin else 'Нет'}\n"
            user_info += "------------------------\n\n"
            
            message += user_info

        # Разбиваем сообщение на части, если оно слишком длинное
        if len(message) > 4096:
            message = message[:4000] + "\n\n(Список слишком длинный и был обрезан)"

        # Добавляем кнопку возврата в админ-панель
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in list_users: {e}")
        await query.edit_message_text("Произошла ошибка при получении списка пользователей.")
    finally:
        session.close()
        logger.info("list_users function completed")
