from enum import Enum, auto

class RequestType(Enum):
    """Типы запросов в системе"""
    VACATION = auto()       # Отпуск
    ADMIN = auto()          # Административные запросы
    AUTH = auto()           # Аутентификация
    
    @property
    def model_name(self) -> str:
        """Возвращает имя модели для данного типа запроса"""
        return {
            RequestType.VACATION: 'VacationRequest',
            RequestType.ADMIN: None,
            RequestType.AUTH: None
        }[self]
    
    @property
    def approval_done_model(self) -> str:
        """Возвращает имя модели завершенного утверждения"""
        return {
            RequestType.VACATION: 'ApprovalDone',
            RequestType.ADMIN: None,
            RequestType.AUTH: None
        }[self]
    
    @property
    def handler_module(self) -> str:
        """Возвращает имя модуля для обработки данного типа запроса"""
        return {
            RequestType.VACATION: 'vacation',
            RequestType.ADMIN: 'admin',
            RequestType.AUTH: 'auth'
        }[self]
