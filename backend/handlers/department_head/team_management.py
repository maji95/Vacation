from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, Department
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def manage_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает панель управления командой"""
    logger.info("Executing manage_team function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права начальника отдела
        head = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not head or head.role.name != "Начальник отдела":
            await query.edit_message_text("У вас нет прав начальника отдела.")
            return

        # Получаем сотрудников отдела
        team_members = session.query(User).filter_by(department_id=head.department_id).all()
        
        message = f"Сотрудники отдела {head.department.name}:\n\n"
        for member in team_members:
            if member.id != head.id:  # Пропускаем самого начальника
                message += f"👤 {member.full_name}\n"
                message += f"   Дней отпуска: {member.vacation_days}\n\n"

        keyboard = [
            [InlineKeyboardButton("График отпусков", callback_data="team_schedule")],
            [InlineKeyboardButton("« Назад", callback_data="department_head_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_team: {e}")
        await query.edit_message_text("Произошла ошибка при открытии управления командой.")
    finally:
        session.close()
        logger.info("manage_team function completed")

async def view_team_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает график отпусков команды"""
    logger.info("Executing view_team_schedule function")
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Проверяем права начальника отдела
        head = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not head or head.role.name != "Начальник отдела":
            await query.edit_message_text("У вас нет прав начальника отдела.")
            return

        # Здесь будет логика отображения графика отпусков
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="manage_team")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Функция просмотра графика отпусков в разработке",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error in view_team_schedule: {e}")
        await query.edit_message_text("Произошла ошибка при открытии графика отпусков.")
    finally:
        session.close()
        logger.info("view_team_schedule function completed")
