import pymysql
import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vacation_service.settings')
django.setup()

# Подключение к базе данных
conn = pymysql.connect(
    host=settings.DATABASES['default']['HOST'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    database=settings.DATABASES['default']['NAME'],
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        # Получаем информацию о структуре таблицы users
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        print("Структура таблицы users:")
        for column in columns:
            print(column)
        
        # Проверяем первую запись в таблице users
        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        if user:
            print("\nПример записи в таблице users:")
            print(user)
        else:
            print("\nТаблица users пуста")
            
except Exception as e:
    print(f"Ошибка: {e}")
    
finally:
    conn.close()
