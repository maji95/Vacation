from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest
from ..admin.system_monitor import SystemMonitor
from ..approval.create_request import create_approval_request, send_approval_request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def vacation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало запроса отпуска"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            await query.edit_message_text("Пользователь не найден.")
            return

        # Логируем начало запроса отпуска
        await SystemMonitor.log_action(
            context,
            "vacation_start",
            user.telegram_id,
            f"Начат процесс запроса отпуска пользователем {user.full_name}"
        )

        keyboard = [
            [InlineKeyboardButton("Запросить отпуск", callback_data="vacation_by_days")],
            [InlineKeyboardButton("« Назад", callback_data="show_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💡 У вас доступно {int(user.vacation_days)} дней отпуска.\n\n"
            "Нажмите кнопку ниже, чтобы начать запрос отпуска:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in vacation_request: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()

async def vacation_by_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отпуска по дням"""
    logger.info("Executing vacation_by_days function")
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("« Назад", callback_data="vacation_request")]]
    await query.edit_message_text(
        "Введите дату начала отпуска в формате ДД.ММ.ГГГГ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['vacation_state'] = 'waiting_start_date'

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в предыдущее меню"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем состояние
    context.user_data.clear()
    
    # Возвращаемся к выбору типа отпуска
    await vacation_request(update, context)

async def restart_vacation_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезапуск запроса отпуска"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем состояние
    context.user_data.clear()
    
    # Возвращаемся к запросу отпуска по дням
    await vacation_by_days(update, context)

async def confirm_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение запроса на отпуск"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            await query.edit_message_text("Пользователь не найден.")
            return

        # Получаем сохраненные данные из контекста
        start_date = context.user_data.get('start_date')
        end_date = context.user_data.get('end_date')
        vacation_days = context.user_data.get('vacation_days')

        if not all([start_date, end_date, vacation_days]):
            await query.edit_message_text(
                "Ошибка: данные о запросе отпуска не найдены. Пожалуйста, начните заново.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="show_menu")
                ]])
            )
            return

        # Создаем запись в базе данных
        vacation_request = VacationRequest(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
            status='pending'
        )
        session.add(vacation_request)
        session.commit()
        logger.info(f"Создан запрос на отпуск для пользователя {user.full_name} (ID: {user.id})")

        # Создаем запись в таблицах утверждения
        success = await create_approval_request(vacation_request.id)
        if success:
            await send_approval_request(update, context, vacation_request.id)
            await query.edit_message_text(
                f"✅ Ваш запрос на отпуск успешно создан и отправлен на рассмотрение:\n\n"
                f"📅 Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
                f"📊 Количество дней: {vacation_days}\n\n"
                f"Вы получите уведомление после рассмотрения запроса.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="show_menu")
                ]])
            )
        else:
            # Если не удалось создать запись в таблицах утверждения
            session.delete(vacation_request)
            session.commit()
            await query.edit_message_text(
                "❌ Произошла ошибка при создании запроса на отпуск. Пожалуйста, попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« В главное меню", callback_data="show_menu")
                ]])
            )

        # Очищаем данные из контекста
        context.user_data.clear()

    except Exception as e:
        logger.error(f"Error in confirm_vacation: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке запроса.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« В главное меню", callback_data="show_menu")
            ]])
        )
    finally:
        session.close()

async def process_vacation_message(update, context):
    """Обрабатывает текстовые сообщения в процессе запроса отпуска"""
    user_data = context.user_data
    message_text = update.message.text
    
    if 'vacation_state' not in user_data:
        await update.message.reply_text(
            "Пожалуйста, начните запрос отпуска через меню бота."
        )
        return
    
    state = user_data['vacation_state']
    
    if state == 'waiting_start_date':
        # Обработка ввода даты начала отпуска
        try:
            start_date = datetime.strptime(message_text, '%d.%m.%Y').date()
            today = datetime.now().date()
            
            if start_date < today:
                await update.message.reply_text(
                    "Дата начала отпуска не может быть в прошлом. Пожалуйста, введите корректную дату:"
                )
                return
                
            user_data['start_date'] = start_date
            user_data['vacation_state'] = 'waiting_end_date'
            
            # Создаем кнопку "Назад"
            keyboard = [[InlineKeyboardButton("« Назад", callback_data="restart_vacation_request")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Дата начала отпуска: {start_date.strftime('%d.%m.%Y')}\n\n"
                "Теперь введите дату окончания отпуска в формате ДД.ММ.ГГГГ:",
                reply_markup=reply_markup
            )
        except ValueError:
            await update.message.reply_text(
                "Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:"
            )
    
    elif state == 'waiting_end_date':
        # Обработка ввода даты окончания отпуска
        try:
            end_date = datetime.strptime(message_text, '%d.%m.%Y').date()
            start_date = user_data['start_date']
            
            if end_date < start_date:
                await update.message.reply_text(
                    "Дата окончания отпуска не может быть раньше даты начала. Пожалуйста, введите корректную дату:"
                )
                return
                
            # Вычисляем количество дней отпуска
            vacation_days = (end_date - start_date).days + 1
            
            # Проверяем, есть ли у пользователя достаточно дней отпуска
            session = get_session()
            try:
                user = session.query(User).filter_by(telegram_id=update.message.from_user.id).first()
                if not user:
                    await update.message.reply_text("Пользователь не найден.")
                    return
                    
                if vacation_days > user.vacation_days:
                    await update.message.reply_text(
                        f"У вас недостаточно дней отпуска. Доступно: {int(user.vacation_days)}, запрошено: {vacation_days}.\n"
                        "Пожалуйста, введите другую дату окончания отпуска:"
                    )
                    return
                    
                # Сохраняем данные
                user_data['end_date'] = end_date
                user_data['vacation_days'] = vacation_days
                
                # Создаем клавиатуру для подтверждения
                keyboard = [
                    [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_vacation")],
                    [InlineKeyboardButton("❌ Отменить", callback_data="restart_vacation_request")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"📅 Период отпуска: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
                    f"📊 Количество дней: {vacation_days}\n\n"
                    "Пожалуйста, проверьте данные и подтвердите запрос:",
                    reply_markup=reply_markup
                )
            finally:
                session.close()
        except ValueError:
            await update.message.reply_text(
                "Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:"
            )
    
    else:
        await update.message.reply_text(
            "Неизвестное состояние. Пожалуйста, начните запрос отпуска заново."
        )
        user_data.clear()
