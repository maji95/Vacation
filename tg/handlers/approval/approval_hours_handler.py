from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, HoursRequest, ApprovalProcessHour, ApprovalDoneHour
from .approval_hours_utils import get_local_time, get_approval_chain, logger
from ..admin.system_monitor import SystemMonitor

async def send_next_approval_notification(context: ContextTypes.DEFAULT_TYPE, hours_request, next_level: str):
    """Отправляет уведомление следующему утверждающему"""
    session = get_session()
    try:
        # Получаем процесс утверждения
        approval_process = session.query(ApprovalProcessHour).filter_by(
            employee_name=hours_request.user.full_name
        ).first()
        if not approval_process:
            logger.error(f"Approval process not found for: {hours_request.user.full_name}")
            return False

        # Получаем утверждающего для следующего уровня
        approver_field = f"{next_level}_approval"
        approver_name = getattr(approval_process, approver_field)
        approver = session.query(User).filter_by(full_name=approver_name).first()
        
        if not approver:
            logger.error(f"Next approver not found: {approver_name}")
            return False

        # Определяем уровень утверждения для сообщения
        level_names = {
            'first': 'первичного',
            'second': 'вторичного',
            'final': 'финального'
        }
        level_name = level_names.get(next_level, '')

        # Формируем сообщение
        message = (
            f"📋 Новый запрос на {level_name} утверждение отгула\n"
            f"От: {hours_request.user.full_name}\n"
            f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
            f"Время: {hours_request.start_hour} - {hours_request.end_hour}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Одобрить",
                    callback_data=f"approve_hours_{hours_request.id}_{next_level}"
                ),
                InlineKeyboardButton(
                    "❌ Отклонить",
                    callback_data=f"reject_hours_{hours_request.id}_{next_level}"
                )
            ]
        ]

        await context.bot.send_message(
            chat_id=approver.telegram_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    except Exception as e:
        logger.error(f"Error sending next approval notification: {e}")
        return False
    finally:
        session.close()

async def notify_user(context: ContextTypes.DEFAULT_TYPE, hours_request, is_approved: bool, is_final: bool = False):
    """Отправляет уведомление сотруднику о решении по его запросу"""
    session = get_session()
    try:
        # Получаем сотрудника
        employee = session.query(User).filter_by(id=hours_request.user_id).first()
        if not employee:
            return

        # Отправляем уведомление только если заявка отклонена или это финальное утверждение
        if not is_approved or is_final:
            status = "одобрен" if is_approved else "отклонен"
            message = (
                f"Ваш запрос на отгул {hours_request.date_absence.strftime('%d.%m.%Y')} "
                f"с {hours_request.start_hour} до {hours_request.end_hour} был {status}."
            )

            # Логируем результат утверждения
            await SystemMonitor.log_action(
                context,
                "approval_result",
                employee.telegram_id,
                f"Запрос на отгул {status} (final={is_final})"
            )

            # Отправляем сообщение
            await context.bot.send_message(
                chat_id=employee.telegram_id,
                text=message
            )

    except Exception as e:
        logger.error(f"Error notifying user: {e}")
    finally:
        session.close()

async def notify_hr(context: ContextTypes.DEFAULT_TYPE, hours_request):
    """Отправляет уведомление HR о финально одобренном отгуле"""
    session = get_session()
    try:
        # Получаем всех HR
        hr_users = session.query(User).filter_by(is_hr=True).all()
        if not hr_users:
            return

        message = (
            f"✨ Новый утвержденный отгул\n\n"
            f"👤 Сотрудник: {hours_request.user.full_name}\n"
            f"📅 Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {hours_request.start_hour} - {hours_request.end_hour}\n"
            f"📝 Дата утверждения: {get_local_time().strftime('%d.%m.%Y %H:%M')}"
        )

        # Отправляем уведомление каждому HR
        for hr in hr_users:
            try:
                await context.bot.send_message(
                    chat_id=hr.telegram_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Error sending HR notification to {hr.full_name}: {e}")

    except Exception as e:
        logger.error(f"Error in notify_hr: {e}")
    finally:
        session.close()

async def handle_hours_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: int, level: str, is_approved: bool):
    """Обрабатывает утверждение или отклонение запроса на отгул"""
    query = update.callback_query
    await query.answer()
    
    session = get_session()
    try:
        # Получаем запрос на отгул
        hours_request = session.query(HoursRequest).filter_by(id=request_id).first()
        if not hours_request:
            logger.error(f"Hours request not found: {request_id}")
            await query.edit_message_text("❌ Запрос не найден")
            return False

        # Проверяем статус запроса
        if hours_request.status != 'pending':
            await query.edit_message_text("❌ Этот запрос уже обработан")
            return False

        # Получаем процесс утверждения
        approval_process = session.query(ApprovalProcessHour).filter_by(
            employee_name=hours_request.user.full_name
        ).first()
        if not approval_process:
            logger.error(f"Approval process not found for: {hours_request.user.full_name}")
            await query.edit_message_text("❌ Процесс утверждения не найден")
            return False

        # Проверяем права утверждающего
        approver = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not approver:
            await query.edit_message_text("❌ Утверждающий не найден")
            return False

        # Проверяем, что утверждающий имеет право на этот уровень
        expected_approver = getattr(approval_process, f"{level}_approval")
        if approver.full_name != expected_approver:
            await query.edit_message_text("❌ У вас нет прав для этого действия")
            return False

        # Получаем цепочку утверждения
        approval_chain = get_approval_chain(hours_request.user.full_name)
        current_level_index = approval_chain.index(level)
        is_final = current_level_index == len(approval_chain) - 1

        if not is_approved:
            # Если запрос отклонен
            hours_request.status = 'rejected'
            hours_request.updated_at = get_local_time()
            session.commit()
            
            # Уведомляем сотрудника
            await notify_user(context, hours_request, False, False)
            await query.edit_message_text("❌ Запрос отклонен")
            return True

        if is_final:
            # Если это финальное утверждение
            try:
                # Создаем запись о финальном утверждении
                approval_done = ApprovalDoneHour(
                    name=hours_request.user.full_name,
                    name_approval=approver.full_name,
                    date_absence=hours_request.date_absence,
                    start_hour=hours_request.start_hour,
                    end_hour=hours_request.end_hour,
                    date=get_local_time()
                )
                session.add(approval_done)

                # Обновляем статус запроса
                hours_request.status = 'approved'
                hours_request.updated_at = get_local_time()
                session.commit()

                # Уведомляем всех
                await notify_user(context, hours_request, True, True)
                await notify_hr(context, hours_request)
                await query.edit_message_text("✅ Запрос окончательно утвержден")
                return True

            except Exception as e:
                logger.error(f"Error creating final approval record: {e}")
                await query.edit_message_text("❌ Ошибка при создании записи об утверждении")
                return False
        else:
            # Если это промежуточное утверждение
            next_level = approval_chain[current_level_index + 1]
            
            # Отправляем уведомление следующему утверждающему
            if await send_next_approval_notification(context, hours_request, next_level):
                await query.edit_message_text("✅ Запрос передан на следующий уровень утверждения")
                return True
            else:
                await query.edit_message_text("❌ Ошибка при отправке уведомления")
                return False

    except Exception as e:
        logger.error(f"Error handling hours approval: {e}")
        await query.edit_message_text("❌ Произошла ошибка при обработке запроса")
        return False
    finally:
        session.close()

__all__ = ['handle_hours_approval']
