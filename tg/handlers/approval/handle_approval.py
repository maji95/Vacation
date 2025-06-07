from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone, ApprovalProcess
from datetime import datetime, timezone, timedelta
import logging
from .approval_handler import calculate_vacation_days, send_next_approval_notification
from .approval_utils import check_approval_permissions, notify_hr_managers, notify_employee_approval

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_local_time():
    """Возвращает текущее время в UTC+2"""
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2)))

async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, approval_id: int, level: str, is_approved: bool):
    """Обрабатывает решение утверждающего"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        logger.info(f"Starting approval handling - ID: {approval_id}, Level: {level}, Approved: {is_approved}")
        
        # Получаем запись об утверждении
        approval_class = {
            'first': ApprovalFirst,
            'second': ApprovalSecond,
            'final': ApprovalFinal
        }[level]
        
        approval_entry = session.query(approval_class).get(approval_id)
        if not approval_entry:
            logger.error(f"Approval entry not found - ID: {approval_id}, Level: {level}")
            await query.edit_message_text("Запрос не найден или уже обработан.")
            return

        logger.info(f"Found approval entry - Name: {approval_entry.name}, Approver: {approval_entry.name_approval}")

        # Проверяем, что утверждающий имеет права
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user or user.full_name != approval_entry.name_approval:
            logger.error(f"Permission denied - User: {user.full_name if user else 'None'}, Expected: {approval_entry.name_approval}")
            await query.edit_message_text("У вас нет прав на обработку этого запроса.")
            return

        # Обновляем статус
        approval_entry.status = 'approved' if is_approved else 'rejected'
        approval_entry.date = get_local_time()

        if is_approved:
            # Получаем цепочку утверждения
            approval_process = session.query(ApprovalProcess).filter_by(
                employee_name=approval_entry.name
            ).first()
            
            if not approval_process:
                logger.error(f"ApprovalProcess not found for employee: {approval_entry.name}")
            else:
                logger.info(f"Found ApprovalProcess - First: {approval_process.first_approval}, "
                          f"Second: {approval_process.second_approval}, Final: {approval_process.final_approval}")

            chain = []
            if approval_process and approval_process.first_approval:
                chain.append('first')
            if approval_process and approval_process.second_approval:
                chain.append('second')
            if approval_process and approval_process.final_approval:
                chain.append('final')

            logger.info(f"Approval chain: {chain}")
            
            current_index = chain.index(level)
            next_level = chain[current_index + 1] if current_index + 1 < len(chain) else None

            logger.info(f"Current index: {current_index}, Next level: {next_level}")

            if next_level:
                # Создаем запись для следующего уровня
                next_approval_class = {
                    'first': ApprovalFirst,
                    'second': ApprovalSecond,
                    'final': ApprovalFinal
                }[next_level]

                new_approval = next_approval_class(
                    name=approval_entry.name,
                    name_approval=getattr(approval_process, f'{next_level}_approval'),
                    days=calculate_vacation_days(approval_entry.start_date, approval_entry.end_date),
                    start_date=approval_entry.start_date,
                    end_date=approval_entry.end_date
                )
                session.add(new_approval)
                session.commit()
                logger.info(f"Created next level approval - Level: {next_level}, ID: {new_approval.id}")

                # Отправляем уведомление следующему утверждающему
                await send_next_approval_notification(context, new_approval, next_level)

            else:
                # Переносим в approval_done
                done_approval = ApprovalDone(
                    name=approval_entry.name,
                    name_approval=approval_entry.name_approval,
                    days=calculate_vacation_days(approval_entry.start_date, approval_entry.end_date),
                    start_date=approval_entry.start_date,
                    end_date=approval_entry.end_date,
                    status='approved'
                )
                session.add(done_approval)
                session.commit()
                logger.info(f"Created done approval - ID: {done_approval.id}")
                
                # Если это финальное одобрение, отправляем уведомление HR
                await notify_hr_managers(context, approval_entry)

        session.commit()

        # Отправляем уведомление сотруднику только если заявка отклонена или это финальное утверждение
        is_final = level == 'final' or not is_approved
        if is_final:
            logger.info(f"Sending notification to employee - Final: {is_final}, Approved: {is_approved}")
            await notify_employee_approval(context, approval_entry, is_approved)

        # Обновляем сообщение у утверждающего с полной информацией
        level_names = {
            'first': 'Первичное',
            'second': 'Вторичное',
            'final': 'Финальное'
        }
        level_name = level_names.get(level, '')
        status = "✅ Одобрена" if is_approved else "❌ Отклонена"
        
        message = (
            f"{status}\n\n"
            f"📋 {level_name} утверждение\n"
            f"👤 Сотрудник: {approval_entry.name}\n"
            f"📅 Период: {approval_entry.start_date.strftime('%d.%m.%Y')} - {approval_entry.end_date.strftime('%d.%m.%Y')}\n"
            f"📊 Дней: {int(approval_entry.days)}\n"
            f"⏰ Время обработки: {approval_entry.date.strftime('%d.%m.%Y %H:%M')}"
        )

        if is_approved and next_level:
            message += f"\n\n↗️ Заявка передана на {level_names.get(next_level, '').lower()} утверждение"
        elif is_approved and not next_level:
            message += "\n\n✨ Заявка полностью утверждена"
        
        await query.edit_message_text(message)

    except Exception as e:
        logger.error(f"Error handling approval: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")
        session.rollback()
    finally:
        session.close()
