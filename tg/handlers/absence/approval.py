from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
from config import get_session
from models import (
    User, HoursRequest, 
    ApprovalFirstHour, ApprovalSecondHour, ApprovalFinalHour, 
    ApprovalProcessHour, ApprovalDoneHour
)
import logging

logger = logging.getLogger(__name__)

async def create_absence_approval_request(hours_request_id: int) -> bool:
    """Создает запись в таблицах утверждения для запроса на отсутствие"""
    session = get_session()
    try:
        # Получаем запрос на отсутствие и информацию о пользователе
        hours_request = session.query(HoursRequest).join(User).filter(
            HoursRequest.id == hours_request_id
        ).first()
        
        if not hours_request:
            logger.error(f"Запрос на отсутствие {hours_request_id} не найден")
            return False

        # Создаем записи в таблицах утверждения
        approval_first = ApprovalFirstHour(
            id_hours=hours_request_id,
            name=hours_request.user.full_name,
            date=hours_request.date_absence,
            start_time=hours_request.start_hour,
            end_time=hours_request.end_hour,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        approval_second = ApprovalSecondHour(
            id_hours=hours_request_id,
            name=hours_request.user.full_name,
            date=hours_request.date_absence,
            start_time=hours_request.start_hour,
            end_time=hours_request.end_hour,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        approval_final = ApprovalFinalHour(
            id_hours=hours_request_id,
            name=hours_request.user.full_name,
            date=hours_request.date_absence,
            start_time=hours_request.start_hour,
            end_time=hours_request.end_hour,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        approval_process = ApprovalProcessHour(
            id_hours=hours_request_id,
            original_name=hours_request.user.full_name,
            employee_name=hours_request.user.full_name,
            date=hours_request.date_absence,
            start_time=hours_request.start_hour,
            end_time=hours_request.end_hour,
            status='pending',
            created_at=datetime.utcnow()
        )

        session.add(approval_first)
        session.add(approval_second)
        session.add(approval_final)
        session.add(approval_process)
        session.commit()

        logger.info(f"Созданы записи утверждения для запроса отсутствия {hours_request_id}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при создании записей утверждения: {e}")
        session.rollback()
        return False
    finally:
        session.close()

async def send_absence_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE, hours_request_id: int):
    """Отправляет уведомление о новом запросе на отсутствие утверждающему первого уровня"""
    session = get_session()
    try:
        # Получаем запись первого уровня утверждения
        approval = session.query(ApprovalFirstHour).filter_by(id_hours=hours_request_id).first()
        if not approval:
            logger.error(f"Не найдена запись утверждения для отсутствия {hours_request_id}")
            return

        # Получаем утверждающего
        approver = session.query(User).filter_by(full_name=approval.name_approval).first()
        if not approver or not approver.telegram_id:
            logger.error(f"Утверждающий не найден или не имеет telegram_id")
            return

        # Формируем сообщение
        message = (
            f"📋 Новый запрос на отсутствие от {approval.name}:\n\n"
            f"📅 Дата: {approval.date.strftime('%d.%m.%Y')}\n"
            f"🕐 Время: {approval.start_time.strftime('%H:%M')} - {approval.end_time.strftime('%H:%M')}"
        )

        # Создаем клавиатуру
        keyboard = [
            [
                InlineKeyboardButton("✅ Утвердить", callback_data=f"approve_first_{hours_request_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_first_{hours_request_id}")
            ]
        ]

        # Отправляем сообщение утверждающему
        await context.bot.send_message(
            chat_id=approver.telegram_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        logger.info(f"Отправлен запрос на утверждение отсутствия {hours_request_id}")

    except Exception as e:
        logger.error(f"Ошибка при отправке запроса на утверждение: {e}")
    finally:
        session.close()

async def handle_absence_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: int, level: str, is_approved: bool):
    """Обработка утверждения/отклонения запроса на отсутствие"""
    query = update.callback_query
    await query.answer()
    
    session = get_session()
    try:
        # Получаем запрос на отсутствие
        hours_request = session.query(HoursRequest).get(request_id)
        if not hours_request:
            await query.edit_message_text("Запрос на утверждение не найден")
            return
            
        # Получаем сотрудника
        employee = session.query(User).get(hours_request.user_id)
        if not employee:
            await query.edit_message_text("Сотрудник не найден")
            return
            
        # Получаем процесс утверждения
        approval_process = session.query(ApprovalProcessHour).filter_by(
            employee_name=employee.full_name
        ).first()
        
        if not approval_process:
            await query.edit_message_text("Процесс утверждения не найден")
            return

        # Определяем текущий уровень утверждения и следующий шаг
        if level == 'first':
            current_table = ApprovalFirstHour
            next_approver_name = approval_process.second_approval if approval_process.second_approval else approval_process.final_approval
        elif level == 'second':
            current_table = ApprovalSecondHour
            next_approver_name = approval_process.final_approval
        else:  # final
            current_table = ApprovalFinalHour
            next_approver_name = None

        # Создаем запись в соответствующей таблице утверждения
        approval = current_table(
            name=employee.full_name,
            name_approval=update.effective_user.full_name,
            status='approved' if is_approved else 'rejected',
            date=datetime.utcnow(),
            date_absence=hours_request.date_absence,
            start_hour=hours_request.start_hour,
            end_hour=hours_request.end_hour
        )
        session.add(approval)

        if is_approved:
            if next_approver_name:
                # Находим следующего утверждающего
                next_approver = session.query(User).filter_by(full_name=next_approver_name).first()
                if next_approver and next_approver.telegram_id:
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                "✅ Утвердить", 
                                callback_data=f"approve_absence_{level.replace('first', 'second').replace('second', 'final')}_{request_id}"
                            ),
                            InlineKeyboardButton(
                                "❌ Отклонить", 
                                callback_data=f"reject_absence_{level.replace('first', 'second').replace('second', 'final')}_{request_id}"
                            )
                        ]
                    ]
                    await context.bot.send_message(
                        chat_id=next_approver.telegram_id,
                        text=(
                            f"📋 Запрос на отсутствие от {employee.full_name}:\n\n"
                            f"📅 Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                            f"🕐 Время: {hours_request.start_hour.strftime('%H:%M')} - "
                            f"{hours_request.end_hour.strftime('%H:%M')}"
                        ),
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            else:
                # Финальное утверждение
                hours_request.status = 'approved'
                hours_request.updated_at = datetime.utcnow()
                
                # Создаем запись в ApprovalDoneHour
                done_approval = ApprovalDoneHour(
                    name=employee.full_name,
                    name_approval=update.effective_user.full_name,
                    status='approved',
                    date=datetime.utcnow(),
                    date_absence=hours_request.date_absence,
                    start_hour=hours_request.start_hour,
                    end_hour=hours_request.end_hour
                )
                session.add(done_approval)
                
                # Отправляем уведомление пользователю
                if employee.telegram_id:
                    await context.bot.send_message(
                        chat_id=employee.telegram_id,
                        text=(
                            "✅ Ваш запрос на отсутствие утвержден:\n\n"
                            f"📅 Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                            f"🕐 Время: {hours_request.start_hour.strftime('%H:%M')} - "
                            f"{hours_request.end_hour.strftime('%H:%M')}"
                        )
                    )
                
                # Отправляем уведомление HR
                hr_user = session.query(User).filter_by(role='hr').first()
                if hr_user and hr_user.telegram_id:
                    await context.bot.send_message(
                        chat_id=hr_user.telegram_id,
                        text=(
                            f"ℹ️ Новый утвержденный запрос на отсутствие от {employee.full_name}:\n\n"
                            f"📅 Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                            f"🕐 Время: {hours_request.start_hour.strftime('%H:%M')} - "
                            f"{hours_request.end_hour.strftime('%H:%M')}"
                        )
                    )
        else:
            # Если запрос отклонен
            hours_request.status = 'rejected'
            hours_request.updated_at = datetime.utcnow()
            
            # Отправляем уведомление пользователю
            if employee.telegram_id:
                await context.bot.send_message(
                    chat_id=employee.telegram_id,
                    text=(
                        "❌ Ваш запрос на отсутствие отклонен:\n\n"
                        f"📅 Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                        f"🕐 Время: {hours_request.start_hour.strftime('%H:%M')} - "
                        f"{hours_request.end_hour.strftime('%H:%M')}"
                    )
                )

        session.commit()
        
        # Обновляем сообщение утверждающего
        await query.edit_message_text(
            f"{'✅ Вы утвердили' if is_approved else '❌ Вы отклонили'} запрос на отсутствие:\n\n"
            f"📅 Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
            f"🕐 Время: {hours_request.start_hour.strftime('%H:%M')} - {hours_request.end_hour.strftime('%H:%M')}"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке утверждения: {e}")
        session.rollback()
        await query.edit_message_text("Произошла ошибка при обработке запроса")
    finally:
        session.close()
