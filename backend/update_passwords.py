import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vacation_service.settings')
django.setup()

from vacation.models import User

def update_user_password(full_name, new_password):
    """
    Обновляет пароль пользователя, сохраняя его в открытом виде.
    """
    try:
        user = User.objects.get(full_name=full_name)
        # Сохраняем пароль в открытом виде
        user.password = new_password
        user.save()
        print(f"Пароль для пользователя '{full_name}' успешно обновлен на '{new_password}'.")
        return True
    except User.DoesNotExist:
        print(f"Пользователь с именем '{full_name}' не найден.")
        return False
    except Exception as e:
        print(f"Ошибка при обновлении пароля: {e}")
        return False

def update_all_passwords(default_password='1234'):
    """
    Обновляет пароли всех пользователей на указанный пароль в открытом виде.
    """
    try:
        users = User.objects.all()
        count = 0
        for user in users:
            user.password = default_password
            user.save()
            count += 1
        print(f"Пароли для {count} пользователей успешно обновлены на '{default_password}'.")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении паролей: {e}")
        return False

def create_test_user(full_name, password):
    """
    Создает тестового пользователя с указанным именем и паролем в открытом виде.
    """
    try:
        # Проверяем, существует ли пользователь
        if User.objects.filter(full_name=full_name).exists():
            print(f"Пользователь с именем '{full_name}' уже существует.")
            return update_user_password(full_name, password)
        
        # Создаем нового пользователя
        user = User(full_name=full_name, password=password)
        user.save()
        print(f"Тестовый пользователь '{full_name}' с паролем '{password}' успешно создан.")
        return True
    except Exception as e:
        print(f"Ошибка при создании тестового пользователя: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("1. Обновить пароль конкретного пользователя:")
        print("   python update_passwords.py update <полное_имя> <новый_пароль>")
        print("2. Обновить пароли всех пользователей:")
        print("   python update_passwords.py update_all [пароль_по_умолчанию]")
        print("3. Создать тестового пользователя:")
        print("   python update_passwords.py create <полное_имя> <пароль>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "update" and len(sys.argv) == 4:
        full_name = sys.argv[2]
        new_password = sys.argv[3]
        update_user_password(full_name, new_password)
    elif command == "update_all":
        default_password = sys.argv[2] if len(sys.argv) > 2 else '1234'
        update_all_passwords(default_password)
    elif command == "create" and len(sys.argv) == 4:
        full_name = sys.argv[2]
        password = sys.argv[3]
        create_test_user(full_name, password)
    else:
        print("Неверные аргументы. Используйте команду без аргументов для получения справки.")
