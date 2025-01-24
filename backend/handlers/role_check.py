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

async def check_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверяет роль пользователя и показывает соответствующую информацию"""
    logger.info("Executing check_role function")
    
    # Получаем информацию о пользователе
    user_id = update.message.from_user.id
    session = get_session()
    
    try:
        # Проверяем, существует ли пользователь в базе
        user = session.query(User).filter_by(telegram_id=user_id).first()
        
        if user:
            # Получаем информацию о роли
            role_name = "Не назначена"
            if user.role_id:
                role = session.query(Role).filter_by(id=user.role_id).first()
                if role:
                    role_name = role.name
            
            # Получаем информацию об отделе
            department_name = "Не назначен"
            if user.department_id:
                department = session.query(Department).filter_by(id=user.department_id).first()
                if department:
                    department_name = department.name
            
            # Формируем сообщение с информацией
            message = f"👤 Информация о пользователе:\n"
            message += f"Имя: {user.full_name}\n"
            message += f"Роль: {role_name}\n"
            message += f"Отдел: {department_name}\n"
            message += f"Дней отпуска: {user.vacation_days}\n"
            message += f"Админ: {'Да' if user.is_admin else 'Нет'}"
            
            # Создаем клавиатуру
            keyboard = [
                [InlineKeyboardButton("Показать меню", callback_data="show_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup)
            logger.info(f"Role check completed for user {user.full_name}")
        
        else:
            # Если пользователь не найден, добавляем его в очередь регистрации
            from models import RegistrationQueue
            
            # Проверяем, не находится ли пользователь уже в очереди
            queue_user = session.query(RegistrationQueue).filter_by(telegram_id=user_id).first()
            if not queue_user:
                new_queue_user = RegistrationQueue(
                    telegram_id=user_id,
                    entered_name=update.message.from_user.full_name
                )
                session.add(new_queue_user)
                session.commit()
                
                await update.message.reply_text(
                    "Ваша заявка на регистрацию отправлена администратору. "
                    "Пожалуйста, ожидайте подтверждения."
                )
                logger.info(f"New user {update.message.from_user.full_name} added to registration queue")
            else:
                await update.message.reply_text(
                    "Ваша заявка уже находится на рассмотрении. "
                    "Пожалуйста, ожидайте подтверждения администратора."
                )
                logger.info(f"User {update.message.from_user.full_name} already in registration queue")
    
    except Exception as e:
        logger.error(f"Error in check_role: {e}")
        await update.message.reply_text(
            "Произошла ошибка при проверке роли. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
    
    finally:
        session.close()

def register(application):
    """
    Регистрация обработчиков для role_check
    """
    application.add_handler(CommandHandler("start", check_role))
