from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, telegram_id, full_name, password=None, **extra_fields):
        if not telegram_id:
            raise ValueError('Users must have a telegram_id')
        user = self.model(
            telegram_id=telegram_id,
            full_name=full_name,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(telegram_id, full_name, password, **extra_fields)

# Create your models here.

class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.role_name

class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'departments'
        managed = False

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Убираем поля, которые есть в AbstractUser и не нужны нам
    username = None
    first_name = None
    last_name = None
    email = None
    
    # Наши кастомные поля
    full_name = models.CharField(max_length=100)
    telegram_id = models.BigIntegerField(unique=True)
    vacation_days = models.FloatField(default=0)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    
    is_manager = models.BooleanField(default=False)
    is_hr = models.BooleanField(default=False)
    is_director = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Добавляем обязательные поля от AbstractUser
    password = models.CharField(max_length=128, default='')
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} (Telegram ID: {self.telegram_id})"

class RegistrationQueue(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    entered_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'registration_queue'
        managed = False

    def __str__(self):
        return f"{self.entered_name} (Telegram ID: {self.telegram_id})"

class VacationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vacation_requests'
        managed = False

    def __str__(self):
        return f"Vacation request for {self.user.full_name} ({self.start_date.date()} - {self.end_date.date()})"
