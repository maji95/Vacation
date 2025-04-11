from ..core.base_handler import BaseRequestHandler
from ..core.request_types import RequestType
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest
from ..admin.system_monitor import SystemMonitor
from ..approval.create_request import create_approval_request, send_approval_request
from datetime import datetime
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class VacationHandler(BaseRequestHandler):
    """Обработчик запросов на отпуск"""
    
    def __init__(self, request_type: RequestType):
        super().__init__(request_type)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Начинает процесс запроса отпуска"""
        query = update.callback_query
        await query.answer()

        try:
            user = self.session.query(User).filter_by(telegram_id=query.from_user.id).first()
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
            logger.error(f"Error in vacation_start: {e}")
            await query.edit_message_text("Произошла ошибка при обработке запроса.")
    
    async def process(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Обрабатывает ввод дат отпуска"""
        logger.info("Executing vacation_process function")
        query = update.callback_query
        await query.answer()

        keyboard = [[InlineKeyboardButton("« Назад", callback_data="vacation_request")]]
        await query.edit_message_text(
            "Введите дату начала отпуска в формате ДД.ММ.ГГГГ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['vacation_state'] = 'waiting_start_date'
    
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Подтверждает запрос на отпуск"""
        query = update.callback_query
        await query.answer()

        try:
            user = self.session.query(User).filter_by(telegram_id=query.from_user.id).first()
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
            self.session.add(vacation_request)
            self.session.commit()
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
                self.session.delete(vacation_request)
                self.session.commit()
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
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Отменяет запрос на отпуск"""
        query = update.callback_query
        await query.answer()
        
        # Очищаем состояние
        context.user_data.clear()
        
        # Возвращаемся к выбору типа отпуска
        await self.start(update, context, **kwargs)
