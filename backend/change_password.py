import pymysql
import os
import django
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vacation_service.settings')
django.setup()

# Новый пароль
new_password = 'rm1908'
hashed_password = make_password(new_password)

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
        # Список пользователей для изменения пароля
        cursor.execute("SELECT id, full_name FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("Пользователи не найдены")
        else:
            print("Доступные пользователи:")
            for user_id, full_name in users:
                print(f"ID: {user_id}, Имя: {full_name}")
            
            # Запрос ID пользователя для изменения пароля
            user_id = input("Введите ID пользователя для изменения пароля: ")
            
            # Обновление пароля
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
            conn.commit()
            
            # Проверка обновления
            cursor.execute("SELECT id, full_name FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            
            if updated_user:
                print(f"Пароль успешно изменен для пользователя {updated_user[1]} (ID: {updated_user[0]})")
                print(f"Новый пароль: {new_password}")
            else:
                print(f"Пользователь с ID {user_id} не найден")
    
except Exception as e:
    print(f"Ошибка: {e}")
    
finally:
    conn.close()
