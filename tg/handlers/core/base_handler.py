from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Any, List, Dict, Type

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import get_session
from models import (
    User, ApprovalProcess, 
    ApprovalFirst, ApprovalSecond, ApprovalFinal, ApprovalDone
)
from .request_types import RequestType

class BaseRequestHandler(ABC):
    """Базовый класс для обработки запросов"""
    
    def __init__(self, request_type: RequestType):
        self.request_type = request_type
        self.session = get_session()
    
    @abstractmethod
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Начинает процесс обработки запроса"""
        pass
    
    @abstractmethod
    async def process(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Обрабатывает данные запроса"""
        pass
    
    @abstractmethod
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Подтверждает запрос"""
        pass
    
    @abstractmethod
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        """Отменяет запрос"""
        pass
    
    def __del__(self):
        """Закрывает сессию при уничтожении объекта"""
        if hasattr(self, 'session') and self.session:
            self.session.close()

class BaseApprovalHandler(ABC):
    """Базовый класс для обработки утверждений"""
    
    def __init__(self, request_type: RequestType):
        self.request_type = request_type
        self.session = get_session()
        
        # Определяем модели утверждений в зависимости от типа
        self.first_model = ApprovalFirst
        self.second_model = ApprovalSecond
        self.final_model = ApprovalFinal
        self.done_model = ApprovalDone
    
    async def get_approval_process(self, user: User) -> Optional[ApprovalProcess]:
        """Получает процесс утверждения для пользователя"""
        return self.session.query(ApprovalProcess).filter_by(
            employee_name=user.full_name
        ).first()
    
    def get_level_model(self, level: str) -> Type[Any]:
        """Возвращает модель для конкретного уровня утверждения"""
        return {
            'first': self.first_model,
            'second': self.second_model,
            'final': self.final_model
        }[level]
    
    async def create_approval_record(self, level: str, employee_name: str, approver_name: str, **kwargs) -> Any:
        """Создает запись об утверждении для конкретного уровня"""
        model = self.get_level_model(level)
        record = model(
            name=employee_name,
            name_approval=approver_name,
            **kwargs
        )
        self.session.add(record)
        self.session.commit()
        return record
    
    async def create_done_record(self, employee_name: str, approver_name: str, **kwargs) -> Any:
        """Создает запись о финальном утверждении"""
        record = self.done_model(
            name=employee_name,
            name_approval=approver_name,
            **kwargs
        )
        self.session.add(record)
        self.session.commit()
        return record
    
    @abstractmethod
    async def handle_approval(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                            request_id: int, level: str, is_approved: bool) -> bool:
        """Обрабатывает утверждение или отклонение запроса"""
        pass
    
    @abstractmethod
    async def notify_employee(self, context: ContextTypes.DEFAULT_TYPE, request: Any, 
                            is_approved: bool, is_final: bool = False) -> None:
        """Уведомляет сотрудника о результате"""
        pass
    
    @abstractmethod
    async def notify_hr(self, context: ContextTypes.DEFAULT_TYPE, request: Any) -> None:
        """Уведомляет HR о финальном утверждении"""
        pass
    
    async def create_approval_buttons(self, request_id: int, level: str) -> InlineKeyboardMarkup:
        """Создает кнопки для утверждения/отклонения"""
        prefix = 'vacation'
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Одобрить",
                    callback_data=f"approve_{prefix}_{request_id}_{level}"
                ),
                InlineKeyboardButton(
                    "❌ Отклонить",
                    callback_data=f"reject_{prefix}_{request_id}_{level}"
                )
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
