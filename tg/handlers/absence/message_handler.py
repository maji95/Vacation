from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import logging
from models import HoursRequest, User
from config import get_session

logger = logging.getLogger(__name__)

async def handle_absence_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений для запроса отсутствия"""
    message = update.message
    waiting_for = context.user_data.get('absence_waiting_for')
    
    logger.info("=== НАЧАЛО ОБРАБОТКИ СООБЩЕНИЯ ОТСУТСТВИЯ ===")
    logger.info(f"Получено сообщение: {message.text}")
    logger.info(f"ID пользователя: {update.effective_user.id}")
    logger.info(f"Весь контекст пользователя: {context.user_data}")
    logger.info(f"Текущее состояние ожидания: {waiting_for}")

    if not waiting_for:
        logger.info("Нет активного состояния ожидания для отсутствия, игнорируем сообщение")
        return

    if waiting_for == 'date':
        logger.info("Обрабатываем ввод даты")
        try:
            # Проверяем формат даты
            date = datetime.strptime(message.text, '%d.%m.%Y')
            if date.date() < datetime.now().date():
                logger.info("Введена дата в прошлом")
                await message.reply_text("❌ Дата не может быть в прошлом. Введите дату снова:")
                return
            
            # Сохраняем дату и запрашиваем время начала
            context.user_data['absence_date'] = date
            context.user_data['absence_waiting_for'] = 'start_time'
            logger.info(f"Сохранена дата: {date}")
            logger.info(f"Обновленный контекст: {context.user_data}")
            
            keyboard = [[InlineKeyboardButton("« Отмена", callback_data="absence_request")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            logger.info("Отправляем запрос времени начала")
            await message.reply_text(
                "🕐 Введите время начала в формате ЧЧ:ММ:",
                reply_markup=reply_markup
            )
        except ValueError as e:
            logger.error(f"Ошибка при обработке даты: {e}")
            await message.reply_text("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ:")

    elif waiting_for == 'start_time':
        logger.info("Обрабатываем ввод времени начала")
        try:
            # Проверяем формат времени
            start_time = datetime.strptime(message.text, '%H:%M').time()
            
            # Сохраняем время начала и запрашиваем время окончания
            context.user_data['absence_start_time'] = start_time
            context.user_data['absence_waiting_for'] = 'end_time'
            logger.info(f"Сохранено время начала: {start_time}")
            logger.info(f"Обновленный контекст: {context.user_data}")
            
            keyboard = [[InlineKeyboardButton("« Отмена", callback_data="absence_request")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            logger.info("Отправляем запрос времени окончания")
            await message.reply_text(
                "🕐 Введите время окончания в формате ЧЧ:ММ:",
                reply_markup=reply_markup
            )
        except ValueError as e:
            logger.error(f"Ошибка при обработке времени начала: {e}")
            await message.reply_text("❌ Неверный формат времени. Используйте формат ЧЧ:ММ:")

    elif waiting_for == 'end_time':
        logger.info("Обрабатываем ввод времени окончания")
        try:
            # Проверяем формат времени
            end_time = datetime.strptime(message.text, '%H:%M').time()
            start_time = context.user_data['absence_start_time']
            
            # Проверяем, что время окончания позже времени начала
            if end_time <= start_time:
                logger.info("Время окончания раньше или равно времени начала")
                await message.reply_text("❌ Время окончания должно быть позже времени начала. Введите время окончания снова:")
                return
            
            # Сохраняем время окончания и показываем подтверждение
            context.user_data['absence_end_time'] = end_time
            context.user_data['absence_waiting_for'] = None
            logger.info(f"Сохранено время окончания: {end_time}")
            logger.info(f"Обновленный контекст: {context.user_data}")
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_absence"),
                    InlineKeyboardButton("❌ Отменить", callback_data="absence_request")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            logger.info("Отправляем сообщение подтверждения")
            await message.reply_text(
                f"📋 Подтвердите запрос отсутствия:\n\n"
                f"📅 Дата: {context.user_data['absence_date'].strftime('%d.%m.%Y')}\n"
                f"🕐 Время начала: {start_time.strftime('%H:%M')}\n"
                f"🕐 Время окончания: {end_time.strftime('%H:%M')}\n",
                reply_markup=reply_markup
            )
        except ValueError as e:
            logger.error(f"Ошибка при обработке времени окончания: {e}")
            await message.reply_text("❌ Неверный формат времени. Используйте формат ЧЧ:ММ:")
    
    logger.info("=== КОНЕЦ ОБРАБОТКИ СООБЩЕНИЯ ОТСУТСТВИЯ ===\n")
