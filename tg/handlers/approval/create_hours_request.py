from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import get_session
from models import User, HoursRequest, ApprovalProcess, ApprovalFirstHour, ApprovalSecondHour, ApprovalFinalHour, ApprovalDoneHour
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def create_hours_approval_request(hours_request_id: int):
    """Создает запрос на утверждение отсутствия в соответствующей таблице"""
    session = get_session()
    try:
        hours_request = session.query(HoursRequest).get(hours_request_id)
        employee = session.query(User).get(hours_request.user_id)
        
        # Проверяем сырые данные из базы
        logger.info("Raw database values:")
        result = session.execute("SELECT employee_name FROM approval_process WHERE employee_name = :name", 
                               {"name": employee.full_name})
        for row in result:
            logger.info(f"Direct from DB: '{row[0]}'")
            
        employee_name = employee.full_name.strip()  # Удаляем лишние пробелы
        logger.info(f"Searching approval process for employee: '{employee_name}'")
        
        # Получаем процесс утверждения для сотрудника напрямую из базы
        result = session.execute(
            "SELECT id FROM approval_process WHERE BINARY employee_name = BINARY :name",
            {"name": employee_name}
        ).first()
        
        if result:
            approval_process_id = result[0]
            approval_process = session.query(ApprovalProcess).get(approval_process_id)
            logger.info(f"Found approval process by direct query for: {approval_process.employee_name}")
        else:
            logger.error(f"Approval process not found for employee: '{employee_name}'")
            # Дополнительная диагностика
            all_processes = session.execute("SELECT employee_name FROM approval_process").fetchall()
            logger.info("All employee names in approval_process:")
            for proc in all_processes:
                logger.info(f"Name in DB: '{proc[0]}'")
            return False
            
        # Определяем цепочку утверждения
        chain = []
        if approval_process.first_approval:
            chain.append('first')
        if approval_process.second_approval:
            chain.append('second')
        if approval_process.final_approval:
            chain.append('final')
        
        logger.info(f"Approval chain: {chain}")
        
        if not chain:
            logger.error("No approval chain defined")
            return False

        # Создаем первую запись в цепочке
        first_level = chain[0]
        approval_classes = {
            'first': ApprovalFirstHour,
            'second': ApprovalSecondHour,
            'final': ApprovalFinalHour
        }
        
        try:
            logger.info(f"Creating {first_level} approval record")
            logger.info(f"Approval data: name={employee_name}, approver={getattr(approval_process, f'{first_level}_approval')}")
            logger.info(f"Request data: date={hours_request.date_absence}, start={hours_request.start_hour}, end={hours_request.end_hour}")
            
            # Проверяем существующие записи
            existing = session.query(approval_classes[first_level]).filter_by(
                name=employee_name,
                date_absence=hours_request.date_absence
            ).first()
            
            if existing:
                logger.info(f"Found existing approval record: {existing.id}")
                return True
                
            new_approval = approval_classes[first_level](
                name=employee_name,
                name_approval=getattr(approval_process, f'{first_level}_approval'),
                date_absence=hours_request.date_absence,
                start_hour=hours_request.start_hour,
                end_hour=hours_request.end_hour,
                status='pending'
            )
            
            session.add(new_approval)
            session.flush()  # Получаем ID до коммита
            logger.info(f"Created approval record with ID: {new_approval.id}")
            session.commit()
            logger.info(f"Successfully created {first_level} approval record")
            return True
            
        except Exception as e:
            logger.error(f"Error creating approval record: {e}")
            session.rollback()
            return False
    except Exception as e:
        logger.error(f"Error creating hours approval request: {e}")
        return False
    finally:
        session.close()

async def send_hours_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE, hours_request_id: int):
    """Отправляет уведомление о новом запросе на утверждение отсутствия"""
    try:
        session = get_session()
        hours_request = session.query(HoursRequest).get(hours_request_id)
        if not hours_request:
            logger.error(f"Hours request not found: {hours_request_id}")
            return False
            
        # Находим текущую запись об утверждении
        approvals = {
            'first': ApprovalFirstHour,
            'second': ApprovalSecondHour,
            'final': ApprovalFinalHour
        }
        
        current_approval = None
        for level, model in approvals.items():
            approval = session.query(model).filter_by(
                name=hours_request.user.full_name,
                date_absence=hours_request.date_absence,
                status='pending'
            ).first()
            if approval:
                current_approval = approval
                current_level = level
                break
                
        if not current_approval:
            logger.error("No pending approval found")
            return False
            
        logger.info(f"Found current approval: {current_level}, approver: {current_approval.name_approval}")
        
        # Получаем telegram_id утверждающего
        approver = session.query(User).filter_by(full_name=current_approval.name_approval).first()
        if not approver:
            logger.error(f"Approver not found: {current_approval.name_approval}")
            return False
            
        logger.info(f"Found approver: {approver.full_name} (ID: {approver.telegram_id})")
        
        # Отправляем уведомление утверждающему
        keyboard = [
            [
                InlineKeyboardButton("✅ Утвердить", callback_data=f"approve_absence_{current_level}_{hours_request.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_absence_{current_level}_{hours_request.id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=approver.telegram_id,
            text=(
                f"📋 Новый запрос на отсутствие\n"
                f"От: {hours_request.user.full_name}\n"
                f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                f"Время: {hours_request.start_hour} - {hours_request.end_hour}"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return True

    except Exception as e:
        logger.error(f"Error sending hours approval request: {e}")
        return False
    finally:
        session.close()

async def handle_hours_approval(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: int, level: str, is_approved: bool):
    """Обработка утверждения/отклонения запроса на отсутствие"""
    query = update.callback_query
    await query.answer()
    
    session = get_session()
    try:
        # Получаем запрос на отсутствие
        hours_request = session.query(HoursRequest).get(request_id)
        if not hours_request:
            logger.error(f"Hours request not found: {request_id}")
            await query.edit_message_text("❌ Запрос не найден")
            return False
            
        # Получаем сотрудника
        employee = session.query(User).get(hours_request.user_id)
        if not employee:
            logger.error("Employee not found")
            await query.edit_message_text("❌ Сотрудник не найден")
            return False
            
        # Получаем процесс утверждения
        approval_process = session.query(ApprovalProcess).filter_by(
            employee_name=employee.full_name
        ).first()
        
        if not approval_process:
            logger.error(f"Approval process not found for employee: {employee.full_name}")
            await query.edit_message_text("❌ Процесс утверждения не найден")
            return False

        # Определяем текущий уровень утверждения и следующий шаг
        approval_classes = {
            'first': ApprovalFirstHour,
            'second': ApprovalSecondHour,
            'final': ApprovalFinalHour
        }
        
        next_levels = {
            'first': 'second',
            'second': 'final',
            'final': None
        }
        
        level_names = {
            'first': 'Первый уровень',
            'second': 'Второй уровень',
            'final': 'Финальный уровень'
        }
        
        current_approval = session.query(approval_classes[level]).filter_by(
            name=employee.full_name,
            date_absence=hours_request.date_absence,
            status='pending'
        ).first()
        
        if not current_approval:
            logger.error(f"Current approval record not found for level {level}")
            await query.edit_message_text("❌ Запись об утверждении не найдена")
            return False
            
        # Обновляем статус текущего утверждения
        current_approval.status = 'approved' if is_approved else 'rejected'
        current_approval.updated_at = datetime.utcnow()
        session.commit()
        
        # Создаем запись в approval_done_hour
        try:
            done_record = ApprovalDoneHour(
                id=request_id,
                name=employee.full_name,
                name_approval=update.effective_user.full_name,
                level=level,
                status='approved' if is_approved else 'rejected',
                date=datetime.utcnow(),
                date_absence=hours_request.date_absence,
                start_time=hours_request.start_hour,
                end_time=hours_request.end_hour,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(done_record)
            session.commit()
            logger.info(f"Created approval_done_hour record for request {request_id}")
        except Exception as e:
            logger.error(f"Error creating approval_done_hour record: {e}")
            # Продолжаем выполнение, так как это не критическая ошибка
        
        if is_approved:
            next_level = next_levels[level]
            if next_level:
                # Получаем имя следующего утверждающего
                next_approver_name = getattr(approval_process, f'{next_level}_approval')
                if next_approver_name:
                    # Создаем запись для следующего уровня
                    next_approval = approval_classes[next_level](
                        name=employee.full_name,
                        name_approval=next_approver_name,
                        date_absence=hours_request.date_absence,
                        start_hour=hours_request.start_hour,
                        end_hour=hours_request.end_hour,
                        status='pending'
                    )
                    session.add(next_approval)
                    session.commit()
                    
                    # Отправляем уведомление следующему утверждающему
                    next_approver = session.query(User).filter_by(full_name=next_approver_name).first()
                    if next_approver and next_approver.telegram_id:
                        keyboard = [
                            [
                                InlineKeyboardButton("✅ Утвердить", callback_data=f"approve_absence_{next_level}_{request_id}"),
                                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_absence_{next_level}_{request_id}")
                            ]
                        ]
                        await context.bot.send_message(
                            chat_id=next_approver.telegram_id,
                            text=(
                                f"📋 Запрос на отсутствие ({level_names[next_level]})\n\n"
                                f"От: {employee.full_name}\n"
                                f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                                f"Время: {hours_request.start_hour} - {hours_request.end_hour}\n\n"
                                f"✅ Утверждено: {update.effective_user.full_name}"
                            ),
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
            else:
                # Это было финальное утверждение
                hours_request.status = 'approved'
                hours_request.updated_at = datetime.utcnow()
                session.commit()
                
                # Уведомляем сотрудника
                await context.bot.send_message(
                    chat_id=employee.telegram_id,
                    text=(
                        "✅ Ваш запрос на отсутствие утвержден!\n\n"
                        f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                        f"Время: {hours_request.start_hour} - {hours_request.end_hour}\n\n"
                        f"Утверждающие:\n"
                        f"1. {approval_process.first_approval}\n"
                        + (f"2. {approval_process.second_approval}\n" if approval_process.second_approval else "")
                        + (f"3. {approval_process.final_approval}" if approval_process.final_approval else "")
                    )
                )
                
                # Уведомляем HR
                hr_users = session.query(User).filter_by(is_hr=True).all()
                for hr_user in hr_users:
                    if hr_user.telegram_id:
                        await context.bot.send_message(
                            chat_id=hr_user.telegram_id,
                            text=(
                                "✅ Новый утвержденный запрос на отсутствие\n\n"
                                f"Сотрудник: {employee.full_name}\n"
                                f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                                f"Время: {hours_request.start_hour} - {hours_request.end_hour}\n\n"
                                f"Утверждающие:\n"
                                f"1. {approval_process.first_approval}\n"
                                + (f"2. {approval_process.second_approval}\n" if approval_process.second_approval else "")
                                + (f"3. {approval_process.final_approval}" if approval_process.final_approval else "")
                            )
                        )
        else:
            # Запрос отклонен
            hours_request.status = 'rejected'
            hours_request.updated_at = datetime.utcnow()
            session.commit()
            
            # Уведомляем сотрудника
            await context.bot.send_message(
                chat_id=employee.telegram_id,
                text=(
                    "❌ Ваш запрос на отсутствие отклонен.\n\n"
                    f"Дата: {hours_request.date_absence.strftime('%d.%m.%Y')}\n"
                    f"Время: {hours_request.start_hour} - {hours_request.end_hour}\n\n"
                    f"Отклонено: {update.effective_user.full_name} ({level_names[level]})"
                )
            )
        
        # Обновляем сообщение утверждающего
        status_text = "утвержден" if is_approved else "отклонен"
        level_text = level_names[level].lower()
        await query.edit_message_text(
            f"✅ Запрос {status_text} ({level_text})",
            reply_markup=None
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error handling approval: {e}")
        await query.edit_message_text("❌ Произошла ошибка при обработке запроса")
        return False
    finally:
        session.close()

__all__ = ['create_hours_approval_request', 'send_hours_approval_request', 'handle_hours_approval']
