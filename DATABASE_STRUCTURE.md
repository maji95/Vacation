# Структура базы данных HR_db

## Основные таблицы

### 1. users
Таблица пользователей системы.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `full_name` - полное имя пользователя (CharField, max_length=100)
- `telegram_id` - ID пользователя в Telegram (BigInteger, unique)
- `vacation_days` - количество доступных дней отпуска (FloatField, default=0)
- `department_id` - ID отдела (ForeignKey -> departments)
- `role_id` - ID роли (ForeignKey -> roles)
- `is_manager` - является ли руководителем отдела (Boolean, default=False)
- `is_hr` - является ли HR-менеджером (Boolean, default=False)
- `is_director` - является ли директором (Boolean, default=False)
- `is_admin` - является ли администратором (Boolean, default=False)
- `created_at` - дата создания (DateTimeField, default=now)
- `updated_at` - дата обновления (DateTimeField, auto_now=True)
- Стандартные поля Django:
  - `password` - хеш пароля (CharField, max_length=128)
  - `last_login` - последний вход (DateTimeField, null=True)
  - `is_superuser` - суперпользователь Django (Boolean, default=False)
  - `is_staff` - доступ к админ-панели Django (Boolean, default=False)
  - `is_active` - активен ли пользователь (Boolean, default=True)
  - `date_joined` - дата регистрации (DateTimeField, default=now)

### 2. departments
Таблица отделов компании.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `name` - название отдела (CharField, max_length=100)

### 3. roles
Таблица ролей пользователей.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `role_name` - название роли (CharField, max_length=50, unique)

### 4. vacation_requests
Таблица заявок на отпуск.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `user_id` - ID пользователя (ForeignKey -> users)
- `start_date` - дата начала отпуска (DateTimeField)
- `end_date` - дата окончания отпуска (DateTimeField)
- `status` - статус заявки (CharField, choices=['pending', 'approved', 'rejected'])
- `comments` - комментарии к заявке (TextField, null=True)
- `created_at` - дата создания заявки (DateTimeField, default=now)
- `updated_at` - дата обновления заявки (DateTimeField, auto_now=True)

### 5. name_dictionary
Таблица словаря имен с поддержкой румынских символов.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `original_name` - оригинальное имя с румынскими символами (VARCHAR(200), COLLATE utf8mb4_romanian_ci)
- `latin_name` - латинизированная версия имени (VARCHAR(200), COLLATE utf8mb4_general_ci)
- `department` - отдел сотрудника (VARCHAR(100), COLLATE utf8mb4_romanian_ci)

### 6. approval_process
Таблица процесса утверждения отпусков.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `employee_name` - имя сотрудника (VARCHAR(200), COLLATE utf8mb4_romanian_ci)
- `first_approval` - первая подпись (VARCHAR(200), COLLATE utf8mb4_romanian_ci, null=True)
- `second_approval` - вторая подпись (VARCHAR(200), COLLATE utf8mb4_romanian_ci, null=True)
- `final_approval` - финальное решение (VARCHAR(200), COLLATE utf8mb4_romanian_ci, null=True)
- `reception_info` - информация для рецепции (ENUM('', 'da'), default='')
- `replacement` - информация о замене (VARCHAR(200), COLLATE utf8mb4_romanian_ci, null=True)
- `timekeeper` - табельщик (VARCHAR(200), COLLATE utf8mb4_romanian_ci, null=True)

### 7. registration_queue
Таблица очереди регистрации новых пользователей.
- `id` - уникальный идентификатор (BigAutoField, primary key)
- `telegram_id` - ID пользователя в Telegram (BigInteger, unique)
- `entered_name` - введенное имя пользователя (CharField, max_length=100)
- `created_at` - дата создания записи (DateTimeField, default=now)

## Системные таблицы Django

### 1. django_admin_log
Логи действий в административной панели Django.
- Хранит информацию о всех действиях администраторов в админ-панели
- Используется для аудита и отслеживания изменений

### 2. django_content_type
Таблица типов контента Django.
- Хранит информацию о всех моделях в проекте
- Используется системой авторизации и ORM Django

### 3. django_migrations
История миграций базы данных.
- Отслеживает все примененные миграции
- Используется для управления схемой базы данных

### 4. django_session
Сессии пользователей Django.
- Хранит данные сессий для административной панели
- Используется для аутентификации в админ-панели

## Связи между таблицами

1. `users` -> `departments`: Один отдел может иметь много пользователей
2. `users` -> `roles`: Одна роль может быть у многих пользователей
3. `vacation_requests` -> `users`: У одного пользователя может быть много заявок на отпуск
4. `approval_process` -> `name_dictionary`: Процесс утверждения связан с записью в словаре имен

## Примечания

1. Все ID поля используют тип BigAutoField для поддержки большого количества записей
2. Временные метки (created_at, updated_at) автоматически заполняются
3. Таблица registration_queue используется как промежуточная при регистрации через Telegram
4. Для румынских символов используется кодировка utf8mb4 с соответствующей коллацией
