import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Config:
    # Настройки подключения к базе данных
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://suceava15a:Kiev73@192.168.101.90/HR_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecretkey")  # Для безопасности

# Настройки базы данных
DB_URL = "mysql+pymysql://suceava15a:Kiev73@192.168.101.90/HR_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Токен бота
BOT_TOKEN = "7074106154:AAG5O8GHIKahNCDpZ-loPOQWzoDa5198SK8"

# Базовый класс для моделей
Base = declarative_base()

def get_session():
    return Session()
