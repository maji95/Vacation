from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import ApprovalFirst, ApprovalFinal, ApprovalDone
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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

        final_level = session.query(ApprovalFinal).filter_by(
            name_approval=user.full_name,
            status='pending'
        ).all()

        all_requests = first_level + final_level

        if not all_requests:
            await query.edit_message_text(
                "Нет заявок, ожидающих вашего утверждения",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Назад", callback_data="show_menu")]])
            )
            return

        message = "📋 Заявки на ваше утверждение:\n\n"
        keyboard = []

        for req in all_requests:
            level = 'Первый уровень' if isinstance(req, ApprovalFirst) else 'Финальный уровень'
            message += (
                f"{level}\n"
                f"Сотрудник: {req.name}\n"
                f"Период: {req.start_date.strftime('%d.%m.%Y')} - {req.end_date.strftime('%d.%m.%Y')}\n"
                f"Дней: {req.days}\n\n"
            )
            callback_prefix = 'first' if isinstance(req, ApprovalFirst) else 'final'
            keyboard.append([
                InlineKeyboardButton(f"✅ Одобрить {req.id}", callback_data=f"approve_{callback_prefix}_{req.id}"),
                InlineKeyboardButton(f"❌ Отклонить {req.id}", callback_data=f"reject_{callback_prefix}_{req.id}")
            ])

        keyboard.append([InlineKeyboardButton("« Назад", callback_data="show_menu")])

        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Error in view_pending_requests: {e}")
        await query.edit_message_text("Ошибка при получении списка заявок")
    finally:
        session.close()
