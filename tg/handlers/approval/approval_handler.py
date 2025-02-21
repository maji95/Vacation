from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone, ApprovalProcess
from ..admin.system_monitor import SystemMonitor
from datetime import datetime, date
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def calculate_vacation_days(start_date: date, end_date: date) -> int:
    """Подсчет количества дней отпуска"""
    return (end_date - start_date).days + 1

async def send_next_approval_notification(context: ContextTypes.DEFAULT_TYPE, new_approval, next_level: str):
    """Отправляет уведомление следующему утверждающему"""
    session = get_session()
    try:
        # Получаем утверждающего
        approver = session.query(User).filter_by(full_name=new_approval.name_approval).first()
        if not approver:
            return

        # Определяем уровень утверждения для сообщения
        level_names = {
            'first': 'первичного',
            'second': 'вторичного',
            'final': 'финального'
        }
        level_name = level_names.get(next_level, '')

        # Формируем сообщение
        message = (
            f"📋 Новый запрос на {level_name} утверждение\n"
            f"От: {new_approval.name}\n"
            f"Период: {new_approval.start_date.strftime('%d.%m.%Y')} - {new_approval.end_date.strftime('%d.%m.%Y')}\n"
            f"Дней: {int(new_approval.days)}"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{next_level}_{new_approval.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{next_level}_{new_approval.id}")
            ]
        ]

        await context.bot.send_message(
            chat_id=approver.telegram_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Error sending next approval notification: {e}")
    finally:
        session.close()

async def notify_user(context: ContextTypes.DEFAULT_TYPE, approval_entry, is_approved: bool, is_final: bool = False):
    """Отправляет уведомление сотруднику о решении по его запросу"""
    session = get_session()
    try:
        # Получаем сотрудника
        employee = session.query(User).filter_by(full_name=approval_entry.name).first()
        if not employee:
            return

        # Отправляем уведомление только если заявка отклонена или это финальное утверждение
        if not is_approved or is_final:
            status = "одобрен" if is_approved else "отклонен"
            message = (
                f"Ваш запрос на отпуск с {approval_entry.start_date.strftime('%d.%m.%Y')} "
                f"по {approval_entry.end_date.strftime('%d.%m.%Y')} был {status}."
            )

            # Логируем результат утверждения
            await SystemMonitor.log_action(
                context,
                "approval_result",
                employee.telegram_id,
                f"Запрос на отпуск {status} (final={is_final})"
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

async def notify_hr(context: ContextTypes.DEFAULT_TYPE, approval_entry):
    """Отправляет уведомление HR о финально одобренном отпуске"""
    session = get_session()
    try:
        # Получаем всех HR
        hr_users = session.query(User).filter_by(is_hr=True).all()
        if not hr_users:
            return

        message = (
            f"✨ Новый утвержденный отпуск\n\n"
            f"👤 Сотрудник: {approval_entry.name}\n"
            f"📅 Период: {approval_entry.start_date.strftime('%d.%m.%Y')} - {approval_entry.end_date.strftime('%d.%m.%Y')}\n"
            f"📊 Дней: {int(approval_entry.days)}\n"
            f"⏰ Дата утверждения: {approval_entry.date.strftime('%d.%m.%Y %H:%M')}"
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

# Экспортируем все необходимые функции
__all__ = ['calculate_vacation_days', 'send_next_approval_notification', 'notify_user', 'notify_hr']
