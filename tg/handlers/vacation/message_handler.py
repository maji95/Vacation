from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import get_session
from models import User, VacationRequest
from ..approval.create_request import create_approval_request, send_approval_request
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def calculate_vacation_days(start_date: datetime, end_date: datetime) -> int:
    """Подсчет количества дней отпуска"""
    days = (end_date - start_date).days + 1
    return int(days)

def create_back_button() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой Назад"""
    keyboard = [[InlineKeyboardButton("« Назад", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений для отпусков"""
    logger.info("Executing handle_message function")
    
    vacation_state = context.user_data.get('vacation_state')
    if not vacation_state:
        return

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=update.message.from_user.id).first()
        if not user:
            await update.message.reply_text("Пользователь не найден.")
            return

        if vacation_state == 'waiting_start_date':
            try:
                start_date = datetime.strptime(update.message.text.strip(), "%d.%m.%Y")
                
                # Проверяем, что дата не в прошлом
                if start_date.date() < datetime.now().date():
                    keyboard = create_back_button()
                    await update.message.reply_text(
                        "Дата начала не может быть в прошлом. Введите дату начала снова.",
                        reply_markup=keyboard
                    )
                    return

                context.user_data['start_date'] = start_date
                context.user_data['vacation_state'] = 'waiting_end_date'
                
                keyboard = create_back_button()
                await update.message.reply_text(
                    "Введите дату окончания отпуска в формате ДД.ММ.ГГГГ",
                    reply_markup=keyboard
                )
            except ValueError:
                keyboard = create_back_button()
                await update.message.reply_text(
                    "Неверный формат даты. Используйте формат ДД.ММ.ГГГГ",
                    reply_markup=keyboard
                )

        elif vacation_state == 'waiting_end_date':
            try:
                end_date = datetime.strptime(update.message.text.strip(), "%d.%m.%Y")
                start_date = context.user_data.get('start_date')
                
                if end_date < start_date:
                    keyboard = create_back_button()
                    await update.message.reply_text(
                        "Дата окончания не может быть раньше даты начала. Введите дату окончания снова.",
                        reply_markup=keyboard
                    )
                    return

                # Проверяем количество дней
                vacation_days = calculate_vacation_days(start_date, end_date)
                if vacation_days > user.vacation_days:
                    keyboard = create_back_button()
                    await update.message.reply_text(
                        f"У вас недостаточно дней отпуска. Доступно: {int(user.vacation_days)} дней.\n"
                        f"Запрошено: {vacation_days} дней.\n"
                        "Пожалуйста, выберите другие даты.",
                        reply_markup=keyboard
                    )
                    return

                # Сохраняем данные в контексте для подтверждения
                context.user_data['end_date'] = end_date
                context.user_data['vacation_days'] = vacation_days
                context.user_data['vacation_state'] = 'waiting_confirmation'

                # Показываем сообщение для подтверждения
                keyboard = [
                    [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_vacation")],
                    [InlineKeyboardButton("✏️ Изменить даты", callback_data="restart_vacation_request")],
                    [InlineKeyboardButton("❌ Отменить", callback_data="back_to_menu")]
                ]
                await update.message.reply_text(
                    f"Пожалуйста, проверьте данные запроса на отпуск:\n\n"
                    f"📅 Дата начала: {start_date.strftime('%d.%m.%Y')}\n"
                    f"📅 Дата окончания: {end_date.strftime('%d.%m.%Y')}\n"
                    f"📊 Количество дней: {vacation_days}\n"
                    f"💡 Доступно дней отпуска: {int(user.vacation_days)}\n\n"
                    f"Всё верно?",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except ValueError:
                keyboard = create_back_button()
                await update.message.reply_text(
                    "Неверный формат даты. Используйте формат ДД.ММ.ГГГГ",
                    reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
        await update.message.reply_text(
            "Произошла ошибка при обработке запроса.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.clear()
    finally:
        session.close()
        logger.info("handle_message function completed")
