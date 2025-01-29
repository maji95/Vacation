from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from config import Base
from datetime import datetime

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Role(id={self.id}, role_name='{self.role_name}')>"

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    telegram_id = Column(Integer, unique=True, nullable=False)
    vacation_days = Column(Float, default=0)
    
    # Внешние ключи
    department_id = Column(Integer, ForeignKey('departments.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))
    
    # Флаги ролей и прав
    is_manager = Column(Boolean, default=False)
    is_hr = Column(Boolean, default=False)
    is_director = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)  # Новый флаг администратора
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Добавляем связи
    department = relationship("Department")
    role = relationship("Role")
    vacation_requests = relationship("VacationRequest", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, full_name='{self.full_name}', telegram_id={self.telegram_id}, vacation_days={self.vacation_days})>"

class RegistrationQueue(Base):
    __tablename__ = 'registration_queue'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    entered_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class VacationRequest(Base):
    __tablename__ = 'vacation_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(10), default='pending')
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Добавляем связь с пользователем
    user = relationship("User", back_populates="vacation_requests")

    def __repr__(self):
        return f"<VacationRequest(id={self.id}, user_id={self.user_id}, start_date='{self.start_date}', end_date='{self.end_date}', status='{self.status}')>"
