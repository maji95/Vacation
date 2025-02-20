from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from config import Base
from datetime import datetime

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
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    # Флаги ролей и прав
    is_hr = Column(Boolean, default=False)
    is_director = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Аутентификация
    password = Column(String(255), nullable=True)
    last_login = Column(DateTime, nullable=True)
    date_joined = Column(DateTime, default=datetime.utcnow)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    department = relationship("Department")
    vacation_requests = relationship("VacationRequest", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, full_name='{self.full_name}')>"

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

class NameDictionary(Base):
    __tablename__ = 'name_dictionary'

    id = Column(Integer, primary_key=True)
    original_name = Column(String(100), nullable=False)
    latin_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<NameDictionary(id={self.id}, original_name='{self.original_name}', latin_name='{self.latin_name}')>"

class ApprovalProcess(Base):
    __tablename__ = 'approval_process'

    id = Column(Integer, primary_key=True)
    original_name = Column(String(100), nullable=False)
    employee_name = Column(String(100), nullable=False)
    first_approval = Column(String(100), nullable=True)
    second_approval = Column(String(100), nullable=True)
    final_approval = Column(String(100), nullable=True)
    reception_info = Column(String(255), nullable=True)
    replacement = Column(String(100), nullable=True)
    timekeeper = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<ApprovalProcess(id={self.id}, original_name='{self.original_name}', employee_name='{self.employee_name}')>"
