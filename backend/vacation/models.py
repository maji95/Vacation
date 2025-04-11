from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, full_name, password=None, **extra_fields):
        if not full_name:
            raise ValueError('Users must have a full name')
        
        user = self.model(
            full_name=full_name,
            **extra_fields
        )
        
        # Устанавливаем пароль
        if password:
            user.password = make_password(password)
        else:
            user.set_password('1234')  # Устанавливаем пароль по умолчанию
            
        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(full_name, password, **extra_fields)

class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'departments'
        managed = True

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Убираем поля, которые есть в AbstractUser и не нужны нам
    username = None
    first_name = None
    last_name = None
    email = None
    
    # Наши кастомные поля
    full_name = models.CharField(max_length=100, unique=True)  # Делаем full_name уникальным
    telegram_id = models.BigIntegerField(null=True, blank=True)  # Делаем telegram_id необязательным
    vacation_days = models.FloatField(default=0)
    department = models.CharField(max_length=100, null=True, blank=True)  # Временно меняем на CharField
    
    # Флаги ролей и прав
    is_hr = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    # Аутентификация и временные метки
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'full_name'  # Используем full_name для входа
    REQUIRED_FIELDS = []  # Убираем обязательные поля

    class Meta:
        db_table = 'users'
        managed = True

    def __str__(self):
        return self.full_name

class RegistrationQueue(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    entered_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'registration_queue'
        managed = True

    def __str__(self):
        return f"{self.entered_name} (Telegram ID: {self.telegram_id})"

class VacationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacation_requests')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    vacation_type = models.CharField(max_length=20, default='annual', choices=[
        ('annual', 'Ежегодный'),
        ('unpaid', 'Без сохранения'),
        ('study', 'Учебный')
    ])
    status = models.CharField(max_length=10, default='pending', choices=[
        ('pending', 'Ожидает'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено')
    ])
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vacation_requests'
        managed = True

    def __str__(self):
        return f"Vacation request for {self.user.full_name} ({self.start_date} - {self.end_date})"

class NameDictionary(models.Model):
    original_name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    class Meta:
        db_table = 'name_dictionary'
        managed = True

    def __str__(self):
        return f"{self.original_name} -> {self.latin_name}"

class ApprovalFirst(models.Model):
    name = models.CharField(max_length=100)
    name_approval = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    date = models.DateTimeField(default=timezone.now)
    days = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        db_table = 'approval_first'
        managed = True

    def __str__(self):
        return f"First approval for {self.name} by {self.name_approval}"

class ApprovalSecond(models.Model):
    name = models.CharField(max_length=100)
    name_approval = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    date = models.DateTimeField(default=timezone.now)
    days = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        db_table = 'approval_second'
        managed = True

    def __str__(self):
        return f"Second approval for {self.name} by {self.name_approval}"

class ApprovalFinal(models.Model):
    name = models.CharField(max_length=100)
    name_approval = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    date = models.DateTimeField(default=timezone.now)
    days = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        db_table = 'approval_final'
        managed = True

    def __str__(self):
        return f"Final approval for {self.name} by {self.name_approval}"

class ApprovalDone(models.Model):
    name = models.CharField(max_length=100)
    name_approval = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='approved')
    date = models.DateTimeField(default=timezone.now)
    days = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        db_table = 'approval_done'
        managed = True

    def __str__(self):
        return f"Completed approval for {self.name} by {self.name_approval}"

class ApprovalProcess(models.Model):
    original_name = models.CharField(max_length=100)
    employee_name = models.CharField(max_length=100)
    first_approval = models.CharField(max_length=100, null=True, blank=True)
    second_approval = models.CharField(max_length=100, null=True, blank=True)
    final_approval = models.CharField(max_length=100, null=True, blank=True)
    reception_info = models.CharField(max_length=255, null=True, blank=True)
    replacement = models.CharField(max_length=100, null=True, blank=True)
    timekeeper = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'approval_process'
        managed = True

    def __str__(self):
        return f"Approval process for {self.employee_name}"
