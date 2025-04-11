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
        # Проверяем структуру таблицы vacation_requests
        cursor.execute("DESCRIBE vacation_requests")
        columns = cursor.fetchall()
        
        print("Структура таблицы vacation_requests:")
        for column in columns:
            print(column)
        
        # Проверяем наличие столбца vacation_type
        has_vacation_type = any(column[0] == 'vacation_type' for column in columns)
        
        if not has_vacation_type:
            print("\nСтолбец 'vacation_type' отсутствует. Добавляем его...")
            cursor.execute("""
            ALTER TABLE vacation_requests 
            ADD COLUMN vacation_type VARCHAR(20) DEFAULT 'annual' 
            AFTER end_date
            """)
            conn.commit()
            print("Столбец 'vacation_type' успешно добавлен.")
        else:
            print("\nСтолбец 'vacation_type' уже существует.")
        
        # Проверяем наличие столбца comments
        has_comments = any(column[0] == 'comments' for column in columns)
        
        if not has_comments:
            print("\nСтолбец 'comments' отсутствует. Добавляем его...")
            cursor.execute("""
            ALTER TABLE vacation_requests 
            ADD COLUMN comments TEXT NULL 
            AFTER status
            """)
            conn.commit()
            print("Столбец 'comments' успешно добавлен.")
        else:
            print("\nСтолбец 'comments' уже существует.")
            
except Exception as e:
    print(f"Ошибка: {e}")
    
finally:
    conn.close()
