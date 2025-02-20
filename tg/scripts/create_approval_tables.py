from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import sys
import os

# Добавляем родительскую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_session, Base

# Создаем базовый класс для моделей
#Base = declarative_base()

class ApprovalFirst(Base):
    __tablename__ = 'approval_first'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    name_approval = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')
    date = Column(DateTime, default=datetime.utcnow)
    days = Column(Float)  # Может быть дробным для часов (0.5 дня = 4 часа)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class ApprovalSecond(Base):
    __tablename__ = 'approval_second'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    name_approval = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')
    date = Column(DateTime, default=datetime.utcnow)
    days = Column(Float)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class ApprovalFinal(Base):
    __tablename__ = 'approval_final'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    name_approval = Column(String(100), nullable=False)
    status = Column(String(20), default='pending')
    date = Column(DateTime, default=datetime.utcnow)
    days = Column(Float)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class ApprovalDone(Base):
    __tablename__ = 'approval_done'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    name_approval = Column(String(100), nullable=False)
    status = Column(String(20), default='approved')
    date = Column(DateTime, default=datetime.utcnow)
    days = Column(Float)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

def create_tables():
    """Создает все таблицы в базе данных"""
    try:
        session = get_session()
        engine = session.get_bind()
        Base.metadata.create_all(engine)
        print("Таблицы успешно созданы:")
        print(" - approval_first")
        print(" - approval_second")
        print(" - approval_final")
        print(" - approval_done")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

if __name__ == "__main__":
    create_tables()
