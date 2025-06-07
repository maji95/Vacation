from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone
import logging

logger = logging.getLogger(__name__)

async def view_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает заявки, ожидающие утверждения"""
    query = update.callback_query
    await query.answer()

    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=query.from_user.id).first()
        
        # Ищем заявки где текущий пользователь является утверждающим
        first_level = session.query(ApprovalFirst).filter_by(
            name_approval=user.full_name,
            status='pending'
        ).all()

        second_level = session.query(ApprovalSecond).filter_by(
            name_approval=user.full_name,
            status='pending'
        ).all()

        final_level = session.query(ApprovalFinal).filter_by(
            name_approval=user.full_name,
            status='pending'
        ).all()

        all_requests = first_level + second_level + final_level

        if not all_requests:
            await query.edit_message_text(
                "Нет заявок, ожидающих вашего утверждения",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Назад", callback_data="show_menu")]])
            )
            return

        # Отправляем первое сообщение как ответ на callback
        await query.edit_message_text(
            "📋 Список заявок на утверждение:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Назад", callback_data="show_menu")]])
        )

        # Отправляем отдельное сообщение для каждой заявки
        for req in all_requests:
            if isinstance(req, ApprovalFirst):
                level = 'Первый уровень'
                callback_prefix = 'first'
            elif isinstance(req, ApprovalSecond):
                level = 'Второй уровень'
                callback_prefix = 'second'
            else:
                level = 'Финальный уровень'
                callback_prefix = 'final'

            message = (
                f"📋 {level}\n"
                f"Сотрудник: {req.name}\n"
                f"Период: {req.start_date.strftime('%d.%m.%Y')} - {req.end_date.strftime('%d.%m.%Y')}\n"
                f"Дней: {int(req.days)}"
            )

            keyboard = [
                [
                    InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{callback_prefix}_{req.id}"),
                    InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{callback_prefix}_{req.id}")
                ]
            ]

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        logger.error(f"Error in view_pending_requests: {e}")
        await query.edit_message_text(
            "Ошибка при получении списка заявок",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Назад", callback_data="show_menu")]])
        )
    finally:
        session.close()
