from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest
import logging
from ..approval.approval_utils import check_approval_permissions, notify_hr_managers, notify_employee_request, update_vacation_status

logger = logging.getLogger(__name__)

async def notify_hr_managers(vacation_request):
    """Уведомляет HR-менеджеров об одобренном отпуске"""
    session = get_session()
    try:
        hr_managers = session.query(User).filter_by(is_hr=True).all()
        employee = session.query(User).filter_by(id=vacation_request.user_id).first()
        
        message = (
            f"✅ Новый одобренный отпуск\n"
            f"Сотрудник: {employee.full_name}\n"
            f"Период: {vacation_request.start_date.strftime('%d.%m.%Y')} - "
            f"{vacation_request.end_date.strftime('%d.%m.%Y')}"
        )
        
        for hr in hr_managers:
            try:
                await context.bot.send_message(
                    chat_id=hr.telegram_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления HR {hr.full_name}: {e}")
    finally:
        session.close()

async def handle_vacation_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, vacation_request_id: int):
    """Отправляет запрос на отпуск директору для одобрения"""
    session = get_session()
    try:
        # Получаем запрос на отпуск
        vacation_request = session.query(VacationRequest).filter_by(id=vacation_request_id).first()
        if not vacation_request:
            return
        
        # Находим директоров
        directors = session.query(User).filter_by(is_director=True).all()
        employee = session.query(User).filter_by(id=vacation_request.user_id).first()
        
        # Формируем сообщение
        message = (
            f"🔔 Новый запрос на отпуск\n"
            f"От: {employee.full_name}\n"
            f"Период: {vacation_request.start_date.strftime('%d.%m.%Y')} - "
            f"{vacation_request.end_date.strftime('%d.%m.%Y')}"
        )
        
        # Создаем клавиатуру с кнопками одобрения/отклонения
        keyboard = [
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_vacation_{vacation_request_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_vacation_{vacation_request_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем запрос всем директорам
        for director in directors:
            try:
                await context.bot.send_message(
                    chat_id=director.telegram_id,
                    text=message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке запроса директору {director.full_name}: {e}")
    finally:
        session.close()

async def approve_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик одобрения отпуска директором"""
    query = update.callback_query
    await query.answer()
    
    # Получаем ID запроса из callback_data
    vacation_request_id = int(query.data.split('_')[-1])
    
    session = get_session()
    try:
        # Проверяем права директора
        director = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not await check_approval_permissions(director):
            await query.edit_message_text("У вас нет прав для выполнения этого действия.")
            return
        
        # Обновляем статус запроса
        vacation_request = await update_vacation_status(session, vacation_request_id, 'approved')
        if not vacation_request:
            await query.edit_message_text("Запрос на отпуск не найден или уже обработан.")
            return
        
        # Уведомляем сотрудника
        await notify_employee_request(context, vacation_request, True)
        
        # Уведомляем HR-менеджеров
        await notify_hr_managers(context, vacation_request)
        
        # Обновляем сообщение у директора
        keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
        await query.edit_message_text(
            f"✅ Отпуск для {vacation_request.user.full_name} одобрен.\n"
            f"Период: {vacation_request.start_date.strftime('%d.%m.%Y')} - {vacation_request.end_date.strftime('%d.%m.%Y')}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка при одобрении отпуска: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()

async def reject_vacation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отклонения отпуска директором"""
    query = update.callback_query
    await query.answer()
    
    # Получаем ID запроса из callback_data
    vacation_request_id = int(query.data.split('_')[-1])
    
    session = get_session()
    try:
        # Проверяем права директора
        director = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not await check_approval_permissions(director):
            await query.edit_message_text("У вас нет прав для выполнения этого действия.")
            return
        
        # Обновляем статус запроса
        vacation_request = await update_vacation_status(session, vacation_request_id, 'rejected')
        if not vacation_request:
            await query.edit_message_text("Запрос на отпуск не найден или уже обработан.")
            return
        
        # Уведомляем сотрудника
        await notify_employee_request(context, vacation_request, False)
        
        # Обновляем сообщение у директора
        keyboard = [[InlineKeyboardButton("« В главное меню", callback_data="show_menu")]]
        await query.edit_message_text(
            f"❌ Отпуск для {vacation_request.user.full_name} отклонен.\n"
            f"Период: {vacation_request.start_date.strftime('%d.%m.%Y')} - {vacation_request.end_date.strftime('%d.%m.%Y')}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка при отклонении отпуска: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
    finally:
        session.close()
