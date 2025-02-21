from config import get_session
from models import User, HoursRequest, ApprovalProcess
from .approval_hours_utils import get_local_time, get_approval_chain, get_approval_classes, logger

async def create_hours_approval_request(hours_request_id: int):
    """Создает запрос на утверждение отсутствия в соответствующей таблице"""
    session = get_session()
    try:
        # Получаем запрос на отсутствие
        hours_request = session.query(HoursRequest).get(hours_request_id)
        if not hours_request:
            logger.error(f"Hours request not found: {hours_request_id}")
            return False
            
        # Получаем сотрудника
        employee = session.query(User).get(hours_request.user_id)
        if not employee:
            logger.error("Employee not found")
            return False
            
        logger.info(f"Creating absence request for user: '{employee.full_name}' (ID: {employee.id})")
        
        # Получаем процесс утверждения для сотрудника
        logger.info("Raw database values:")
        direct_query = session.query(User.full_name).filter_by(id=employee.id).first()
        logger.info(f"Direct from DB: '{direct_query[0]}'")
        
        logger.info(f"Searching approval process for employee: '{employee.full_name}'")
        
        approval_process = session.query(ApprovalProcess).filter_by(
            employee_name=employee.full_name
        ).first()
        
        if not approval_process:
            logger.error(f"Approval process not found for employee: {employee.full_name}")
            return False
            
        logger.info(f"Found approval process by direct query for: {approval_process.employee_name}")
        
        # Определяем цепочку утверждения
        chain = get_approval_chain(employee.full_name)
        logger.info(f"Approval chain: {chain}")
        
        if not chain:
            logger.error("Empty approval chain")
            return False
            
        # Создаем запись для первого уровня утверждения
        level = chain[0]
        logger.info("Creating first approval record")
        
        # Получаем имя утверждающего из процесса утверждения
        approver_field = f"{level}_approval"
        approver = getattr(approval_process, approver_field)
        
        logger.info(f"Approval data: name={employee.full_name}, approver={approver}")
        logger.info(f"Request data: date={hours_request.date_absence}, start={hours_request.start_hour}, end={hours_request.end_hour}")
        
        # Создаем запись об утверждении
        approval_classes = get_approval_classes()
        approval = approval_classes[level](
            name=employee.full_name,
            name_approval=approver,
            date_absence=hours_request.date_absence,
            start_hour=hours_request.start_hour,
            end_hour=hours_request.end_hour,
            status='pending',
            date=get_local_time()
        )
        
        session.add(approval)
        session.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating approval record: {e}")
        session.rollback()
        return False
    finally:
        session.close()

__all__ = ['create_hours_approval_request']
