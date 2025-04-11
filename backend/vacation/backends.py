from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class FullNameModelBackend(ModelBackend):
    """
    Аутентификация по полному имени вместо имени пользователя.
    Сравнивает введенный пароль напрямую с паролем в базе данных без хеширования.
    """
    def authenticate(self, request, full_name=None, password=None, **kwargs):
        logger.info(f"FullNameModelBackend: Попытка аутентификации для full_name={full_name}")
        if full_name is None:
            full_name = kwargs.get('username')
            logger.info(f"FullNameModelBackend: full_name не указан, используем username={full_name}")
        
        if full_name is None or password is None:
            logger.warning("FullNameModelBackend: Отсутствует full_name или password")
            return None
        
        try:
            # Получаем пользователя по полному имени
            user = User.objects.get(full_name=full_name)
            logger.info(f"FullNameModelBackend: Пользователь найден: {user}")
            
            # Прямое сравнение паролей
            logger.info(f"FullNameModelBackend: Введенный пароль: {password}")
            logger.info(f"FullNameModelBackend: Пароль в базе данных: {user.password}")
            
            if password == user.password:
                logger.info(f"FullNameModelBackend: Пароль верный для пользователя {full_name}")
                return user
            else:
                logger.warning(f"FullNameModelBackend: Неверный пароль для пользователя {full_name}")
                return None
                
        except User.DoesNotExist:
            logger.warning(f"FullNameModelBackend: Пользователь с именем {full_name} не найден")
        except Exception as e:
            logger.error(f"FullNameModelBackend: Ошибка при аутентификации: {e}")
        
        return None
