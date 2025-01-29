import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vacation_service.settings')

import django
django.setup()

from vacation.models import User

# Получаем пользователя
user = User.objects.get(telegram_id=331885264)
# Устанавливаем пароль
user.set_password('admin123')
user.save()

print("Password has been set successfully!")
