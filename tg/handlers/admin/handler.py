from ..core.base_handler import BaseRequestHandler
from ..core.request_types import RequestType
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, VacationRequest, ApprovalProcess
from .system_monitor import SystemMonitor
import logging
from datetime import datetime, timedelta

# Настройка логирования
logger = logging.getLogger(__name__)

class AdminHandler(BaseRequestHandler):
    """Обработчик административных запросов"""
    
    def __init__(self, request_type: RequestType):
        super().__init__(request_type)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Показывает административное меню"""
        query = update.callback_query
        await query.answer()

        try:
            user = self.session.query(User).filter_by(telegram_id=query.from_user.id).first()
            if not user or not user.is_admin:
                await query.edit_message_text("У вас нет прав администратора.")
                return

            # Логируем доступ к админ-панели
            await SystemMonitor.log_action(
                context,
                "admin_access",
                user.telegram_id,
                f"Администратор {user.full_name} открыл админ-панель"
            )

            keyboard = [
                [InlineKeyboardButton("Управление пользователями", callback_data="admin_users")],
                [InlineKeyboardButton("Статистика запросов", callback_data="admin_stats")],
                [InlineKeyboardButton("Настройки системы", callback_data="admin_settings")],
                [InlineKeyboardButton("« Назад", callback_data="show_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔧 Панель администратора\n\n"
                "Выберите раздел для управления:",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in admin_start: {e}")
            await query.edit_message_text("Произошла ошибка при обработке запроса.")
    
    async def process(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Обрабатывает выбор раздела администрирования"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        
        if action == "admin_users":
            await self._show_users_management(update, context)
        elif action == "admin_stats":
            await self._show_stats(update, context)
        elif action == "admin_settings":
            await self._show_settings(update, context)
        else:
            await query.edit_message_text(
                "Неизвестное действие. Пожалуйста, вернитесь в меню администратора.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="admin_menu")
                ]])
            )
    
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Подтверждает административное действие"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        
        try:
            user = self.session.query(User).filter_by(telegram_id=query.from_user.id).first()
            if not user or not user.is_admin:
                await query.edit_message_text("У вас нет прав администратора.")
                return
                
            # Обработка различных административных действий
            if action.startswith("confirm_add_user_"):
                await self._confirm_add_user(update, context)
            elif action.startswith("confirm_edit_user_"):
                await self._confirm_edit_user(update, context)
            elif action.startswith("confirm_delete_user_"):
                await self._confirm_delete_user(update, context)
            elif action.startswith("confirm_setting_"):
                await self._confirm_setting_change(update, context)
            else:
                await query.edit_message_text(
                    "Неизвестное действие. Пожалуйста, вернитесь в меню администратора.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("« Назад", callback_data="admin_menu")
                    ]])
                )
                
        except Exception as e:
            logger.error(f"Error in admin_confirm: {e}")
            await query.edit_message_text(
                "Произошла ошибка при обработке запроса.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="admin_menu")
                ]])
            )
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Отменяет административное действие"""
        query = update.callback_query
        await query.answer()
        
        # Очищаем состояние
        if 'admin_state' in context.user_data:
            del context.user_data['admin_state']
        
        # Возвращаемся в меню администратора
        await self.start(update, context)
    
    async def _show_users_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню управления пользователями"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("Добавить пользователя", callback_data="admin_add_user")],
            [InlineKeyboardButton("Список пользователей", callback_data="admin_list_users")],
            [InlineKeyboardButton("« Назад", callback_data="admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👥 Управление пользователями\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )
    
    async def _show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает статистику запросов"""
        query = update.callback_query
        
        try:
            # Получаем статистику по отпускам
            vacation_total = self.session.query(VacationRequest).count()
            vacation_pending = self.session.query(VacationRequest).filter_by(status='pending').count()
            vacation_approved = self.session.query(VacationRequest).filter_by(status='approved').count()
            vacation_rejected = self.session.query(VacationRequest).filter_by(status='rejected').count()
            
            # Статистика за последний месяц
            month_ago = datetime.now() - timedelta(days=30)
            vacation_month = self.session.query(VacationRequest).filter(VacationRequest.created_at >= month_ago).count()
            
            keyboard = [
                [InlineKeyboardButton("Подробная статистика", callback_data="admin_detailed_stats")],
                [InlineKeyboardButton("« Назад", callback_data="admin_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📊 Статистика запросов\n\n"
                f"📅 Отпуска:\n"
                f"Всего: {vacation_total}\n"
                f"Ожидают: {vacation_pending}\n"
                f"Одобрено: {vacation_approved}\n"
                f"Отклонено: {vacation_rejected}\n\n"
                f"📈 За последний месяц:\n"
                f"Отпуска: {vacation_month}",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in _show_stats: {e}")
            await query.edit_message_text(
                "Произошла ошибка при получении статистики.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("« Назад", callback_data="admin_menu")
                ]])
            )
    
    async def _show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает настройки системы"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("Настройки утверждения", callback_data="admin_approval_settings")],
            [InlineKeyboardButton("Настройки уведомлений", callback_data="admin_notification_settings")],
            [InlineKeyboardButton("« Назад", callback_data="admin_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ Настройки системы\n\n"
            "Выберите категорию настроек:",
            reply_markup=reply_markup
        )
    
    # Вспомогательные методы для управления пользователями
    async def _confirm_add_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждает добавление нового пользователя"""
        # Реализация добавления пользователя
        pass
        
    async def _confirm_edit_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждает редактирование пользователя"""
        # Реализация редактирования пользователя
        pass
        
    async def _confirm_delete_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждает удаление пользователя"""
        # Реализация удаления пользователя
        pass
        
    async def _confirm_setting_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждает изменение настройки"""
        # Реализация изменения настройки
        pass
