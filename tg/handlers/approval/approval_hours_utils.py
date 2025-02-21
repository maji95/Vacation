from datetime import datetime, timezone, timedelta
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_local_time():
    """Возвращает текущее время в UTC+2"""
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2)))

def get_approval_chain(employee_name):
    """Определяет цепочку утверждения на основе процесса"""
    # Для отгулов используем стандартную цепочку утверждения
    return ['first', 'second', 'final']

def get_approval_classes():
    """Возвращает словарь классов утверждения"""
    from models import ApprovalFirstHour, ApprovalSecondHour, ApprovalFinalHour
    return {
        'first': ApprovalFirstHour,
        'second': ApprovalSecondHour,
        'final': ApprovalFinalHour
    }

__all__ = ['get_local_time', 'get_approval_chain', 'get_approval_classes', 'logger']
