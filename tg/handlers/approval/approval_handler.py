from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest, ApprovalProcess, ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def create_approval_request(vacation_request_id: int):
    """Создает запрос на утверждение в соответствующей таблице"""
    session = get_session()
    try:
        vacation_request = session.query(VacationRequest).get(vacation_request_id)
        employee = session.query(User).get(vacation_request.user_id)
        
        # Получаем процесс утверждения для сотрудника
        approval_process = session.query(ApprovalProcess).filter_by(
            employee_name=employee.full_name
        ).first()

        if approval_process:
            # Определяем цепочку утверждения
            chain = []
            if approval_process.first_approval:
                chain.append('first')
            if approval_process.second_approval:
                chain.append('second')
            if approval_process.final_approval:
                chain.append('final')
            
            if not chain:
                return False

            # Создаем первую запись в цепочке
            first_level = chain[0]
            new_approval = {
                'first': ApprovalFirst,
                'second': ApprovalSecond,
                'final': ApprovalFinal
            }[first_level](
                name=employee.full_name,
                name_approval=getattr(approval_process, f'{first_level}_approval'),
                days=(vacation_request.end_date - vacation_request.start_date).days,
                start_date=vacation_request.start_date,
                end_date=vacation_request.end_date
            )
            
            session.add(new_approval)
            session.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Error creating approval request: {e}")
        return False
    finally:
        session.close()

async def send_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE, approval_entry, level: str):
    """Отправляет запрос на утверждение соответствующему пользователю"""
    session = get_session()
    try:
        approver = session.query(User).filter_by(full_name=approval_entry.name_approval).first()
        
        if not approver:
            return False

        message = (
            f"🔔 Новый запрос на утверждение ({level} уровень)\n"
            f"Сотрудник: {approval_entry.name}\n"
            f"Период: {approval_entry.start_date.strftime('%d.%m.%Y')} - "
            f"{approval_entry.end_date.strftime('%d.%m.%Y')}\n"
            f"Дней: {approval_entry.days}"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{level}_{approval_entry.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{level}_{approval_entry.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=approver.telegram_id,
            text=message,
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        logger.error(f"Error sending approval request: {e}")
        return False
    finally:
        session.close()

async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, approval_id: int, level: str, is_approved: bool):
    """Обрабатывает решение утверждающего"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        # Получаем запись об утверждении
        approval_class = {
            'first': ApprovalFirst,
            'second': ApprovalSecond,
            'final': ApprovalFinal
        }[level]
        
        approval_entry = session.query(approval_class).get(approval_id)
        if not approval_entry:
            return

        # Обновляем статус
        approval_entry.status = 'approved' if is_approved else 'rejected'
        approval_entry.date = datetime.utcnow()

        if is_approved:
            # Получаем цепочку утверждения
            approval_process = session.query(ApprovalProcess).filter_by(
                employee_name=approval_entry.name
            ).first()

            chain = []
            if approval_process.first_approval:
                chain.append('first')
            if approval_process.second_approval:
                chain.append('second')
            if approval_process.final_approval:
                chain.append('final')

            current_index = chain.index(level)
            next_level = chain[current_index + 1] if current_index + 1 < len(chain) else None

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
                    days=approval_entry.days,
                    start_date=approval_entry.start_date,
                    end_date=approval_entry.end_date
                )
                session.add(new_approval)

            else:
                # Переносим в approval_done
                done_approval = ApprovalDone(
                    name=approval_entry.name,
                    name_approval=approval_entry.name_approval,
                    days=approval_entry.days,
                    start_date=approval_entry.start_date,
                    end_date=approval_entry.end_date
                )
                session.add(done_approval)

        session.commit()

        # Отправляем уведомление сотруднику
        await notify_user(approval_entry, is_approved)

        # Обновляем сообщение у утверждающего
        await query.edit_message_text(
            text=f"Заявка {'одобрена' if is_approved else 'отклонена'}!",
            reply_markup=None
        )

    except Exception as e:
        logger.error(f"Error handling approval: {e}")
        session.rollback()
    finally:
        session.close()
