import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
load_dotenv()

class Config:
    # Настройки подключения к базе данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://default:password@localhost/default_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")  # Для безопасности

# Настройки базы данных
DB_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://default:password@localhost/default_db')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '7074106154:AAG5O8GHIKahNCDpZ-loPOQWzoDa5198SK8')

# Базовый класс для моделей
Base = declarative_base()

def get_session():
    return Session()
