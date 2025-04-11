import os
import django
import pymysql
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
        
        # Проверяем типы полей start_date и end_date
        start_date_type = next((column[1] for column in columns if column[0] == 'start_date'), None)
        end_date_type = next((column[1] for column in columns if column[0] == 'end_date'), None)
        
        print(f"\nТип поля start_date: {start_date_type}")
        print(f"Тип поля end_date: {end_date_type}")
        
        # Проверяем наличие данных в таблице
        cursor.execute("SELECT COUNT(*) as count FROM vacation_requests")
        count = cursor.fetchone()[0]
        print(f"\nКоличество записей в таблице: {count}")
        
        if count > 0:
            # Выводим несколько записей для проверки
            cursor.execute("SELECT id, user_id, start_date, end_date, status FROM vacation_requests LIMIT 5")
            records = cursor.fetchall()
            print("\nПримеры записей:")
            for record in records:
                print(record)
        
        print("\nРекомендации:")
        if start_date_type == 'date' and end_date_type == 'date':
            print("1. Измените модель VacationRequest, заменив DateTimeField на DateField для полей start_date и end_date")
            print("2. Обновите все места в коде, где обрабатываются эти поля, чтобы учесть, что они теперь имеют тип date, а не datetime")
        else:
            print("Типы полей в базе данных не соответствуют ожидаемым. Требуется дополнительный анализ.")
            
except Exception as e:
    print(f"Ошибка: {e}")
    
finally:
    conn.close()
