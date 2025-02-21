import sys
import os

# Добавляем родительскую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, Integer, String, DateTime, Time, Text, ForeignKey, MetaData, Table
from config import get_session

def create_tables():
    """Создание таблиц для запросов на отсутствие"""
    try:
        session = get_session()
        metadata = MetaData()
        
        # Загружаем информацию о существующих таблицах
        metadata.reflect(bind=session.get_bind())
        
        # Таблица hours_request
        hours_request = Table('hours_request', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
            Column('date_absence', DateTime, nullable=False),
            Column('start_hour', Time, nullable=False),
            Column('end_hour', Time, nullable=False),
            Column('status', String(10), default='pending'),
            Column('comments', Text, nullable=True),
            Column('created_at', DateTime),
            Column('updated_at', DateTime)
        )

        # Таблица approval_first_hour
        approval_first_hour = Table('approval_first_hour', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', String(100), nullable=False),
            Column('name_approval', String(100), nullable=False),
            Column('status', String(20), default='pending'),
            Column('date', DateTime),
            Column('date_absence', DateTime, nullable=False),
            Column('start_hour', Time, nullable=False),
            Column('end_hour', Time, nullable=False)
        )

        # Таблица approval_second_hour
        approval_second_hour = Table('approval_second_hour', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', String(100), nullable=False),
            Column('name_approval', String(100), nullable=False),
            Column('status', String(20), default='pending'),
            Column('date', DateTime),
            Column('date_absence', DateTime, nullable=False),
            Column('start_hour', Time, nullable=False),
            Column('end_hour', Time, nullable=False)
        )

        # Таблица approval_final_hour
        approval_final_hour = Table('approval_final_hour', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', String(100), nullable=False),
            Column('name_approval', String(100), nullable=False),
            Column('status', String(20), default='pending'),
            Column('date', DateTime),
            Column('date_absence', DateTime, nullable=False),
            Column('start_hour', Time, nullable=False),
            Column('end_hour', Time, nullable=False)
        )

        # Таблица approval_done_hour
        approval_done_hour = Table('approval_done_hour', metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', String(100), nullable=False),
            Column('name_approval', String(100), nullable=False),
            Column('status', String(20), default='approved'),
            Column('date', DateTime),
            Column('date_absence', DateTime, nullable=False),
            Column('start_hour', Time, nullable=False),
            Column('end_hour', Time, nullable=False)
        )

        # Таблица approval_process_hour
        approval_process_hour = Table('approval_process_hour', metadata,
            Column('id', Integer, primary_key=True),
            Column('original_name', String(100), nullable=False),
            Column('employee_name', String(100), nullable=False),
            Column('first_approval', String(100)),
            Column('second_approval', String(100)),
            Column('final_approval', String(100)),
            Column('reception_info', String(255)),
            Column('replacement', String(100)),
            Column('timekeeper', String(100))
        )

        # Создаем таблицы
        metadata.create_all(bind=session.get_bind())
        print("Таблицы для запросов на отсутствие успешно созданы!")
        
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

if __name__ == "__main__":
    create_tables()
