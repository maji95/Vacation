from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from datetime import datetime
import logging
from models import HoursRequest, User
from config import get_session

# Состояния разговора
WAITING_DATE = 1
WAITING_START_TIME = 2
WAITING_END_TIME = 3
WAITING_CONFIRMATION = 4  # Новое состояние для подтверждения

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def absence_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало запроса отсутствия - запрос даты"""
    query = update.callback_query
    await query.answer()

    logger.info("=== НАЧАЛО ЗАПРОСА ОТСУТСТВИЯ ===")
    logger.info(f"ID пользователя: {update.effective_user.id}")
    
    # Отправляем новое сообщение вместо редактирования старого
    keyboard = [[InlineKeyboardButton("« Отмена", callback_data="cancel_absence")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    logger.info("Отправляем запрос даты")
    await query.message.reply_text(
        "📅 Введите дату отсутствия в формате ДД.ММ.ГГГГ:",
        reply_markup=reply_markup
    )
    # Удаляем старое сообщение
    await query.message.delete()
    
    return WAITING_DATE

async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка введенной даты"""
    message = update.message
    try:
        # Проверяем формат даты
        date = datetime.strptime(message.text, '%d.%m.%Y')
        if date.date() < datetime.now().date():
            await message.reply_text("❌ Дата не может быть в прошлом. Введите дату снова:")
            return WAITING_DATE
        
        # Сохраняем дату и запрашиваем время начала
        context.user_data['absence_date'] = date
        logger.info(f"Сохранена дата: {date}")
        
        keyboard = [[InlineKeyboardButton("« Отмена", callback_data="cancel_absence")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            "🕐 Введите время начала в формате ЧЧ:ММ:",
            reply_markup=reply_markup
        )
        return WAITING_START_TIME
        
    except ValueError as e:
        logger.error(f"Ошибка при обработке даты: {e}")
        await message.reply_text("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ:")
        return WAITING_DATE

async def handle_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка времени начала"""
    message = update.message
    try:
        # Проверяем формат времени
        start_time = datetime.strptime(message.text, '%H:%M').time()
        
        # Сохраняем время начала и запрашиваем время окончания
        context.user_data['absence_start_time'] = start_time
        logger.info(f"Сохранено время начала: {start_time}")
        
        keyboard = [[InlineKeyboardButton("« Отмена", callback_data="cancel_absence")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            "🕐 Введите время окончания в формате ЧЧ:ММ:",
            reply_markup=reply_markup
        )
        return WAITING_END_TIME
        
    except ValueError as e:
        logger.error(f"Ошибка при обработке времени начала: {e}")
        await message.reply_text("❌ Неверный формат времени. Используйте формат ЧЧ:ММ:")
        return WAITING_START_TIME

async def handle_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка времени окончания"""
    message = update.message
    try:
        # Проверяем формат времени
        end_time = datetime.strptime(message.text, '%H:%M').time()
        start_time = context.user_data['absence_start_time']
        
        # Проверяем, что время окончания позже времени начала
        if end_time <= start_time:
            await message.reply_text("❌ Время окончания должно быть позже времени начала. Введите время окончания снова:")
            return WAITING_END_TIME
        
        # Сохраняем время окончания и показываем подтверждение
        context.user_data['absence_end_time'] = end_time
        logger.info(f"Сохранено время окончания: {end_time}")
        
        # Рассчитываем время отсутствия
        start_datetime = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)
        duration = end_datetime - start_datetime
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_absence"),
                InlineKeyboardButton("❌ Отменить", callback_data="cancel_absence")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Формируем строку с временем отсутствия
        duration_str = ""
        if hours > 0:
            duration_str += f"{hours} ч"
        if minutes > 0:
            if duration_str:
                duration_str += " "
            duration_str += f"{minutes} мин"
        
        await message.reply_text(
            f"📋 Подтвердите запрос отсутствия:\n\n"
            f"📅 Дата: {context.user_data['absence_date'].strftime('%d.%m.%Y')}\n"
            f"🕐 Время начала: {start_time.strftime('%H:%M')}\n"
            f"🕐 Время окончания: {end_time.strftime('%H:%M')}\n"
            f"⏱ Время отсутствия: {duration_str}",
            reply_markup=reply_markup
        )
        return WAITING_CONFIRMATION
        
    except ValueError as e:
        logger.error(f"Ошибка при обработке времени окончания: {e}")
        await message.reply_text("❌ Неверный формат времени. Используйте формат ЧЧ:ММ:")
        return WAITING_END_TIME

async def cancel_absence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена запроса отсутствия"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем данные
    context.user_data.clear()
    
    # Показываем сообщение об отмене
    keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "❌ Запрос на отсутствие отменен.",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def confirm_absence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение и сохранение запроса отсутствия"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Получаем пользователя
        session = get_session()
        user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            raise ValueError("Пользователь не найден")
        
        logger.info(f"Создаем запрос отсутствия для пользователя {user.id}")
        
        # Создаем объект запроса
        hours_request = HoursRequest(
            user_id=user.id,
            date_absence=context.user_data['absence_date'],
            start_hour=context.user_data['absence_start_time'],
            end_hour=context.user_data['absence_end_time'],
            status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(hours_request)
        session.commit()
        logger.info(f"Запрос отсутствия создан: {hours_request.id}")
        
        # Очищаем данные
        context.user_data.clear()
        logger.info("Контекст очищен")
        
        # Показываем сообщение об успехе
        keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "✅ Запрос на отсутствие успешно создан и отправлен на рассмотрение.",
            reply_markup=reply_markup
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка при создании запроса отсутствия: {e}")
        keyboard = [[InlineKeyboardButton("« Назад", callback_data="absence_request")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❌ Произошла ошибка при создании запроса. Пожалуйста, попробуйте снова.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    finally:
        session.close()
