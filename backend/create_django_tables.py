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
        # Создаем таблицы для Django auth
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `auth_permission` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `name` varchar(255) NOT NULL,
            `content_type_id` int(11) NOT NULL,
            `codename` varchar(100) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `auth_permission_content_type_id_codename` (`content_type_id`,`codename`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `auth_group` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `name` varchar(150) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `name` (`name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `group_id` int(11) NOT NULL,
            `permission_id` int(11) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `auth_group_permissions_group_id_permission_id` (`group_id`,`permission_id`),
            KEY `auth_group_permissions_group_id` (`group_id`),
            KEY `auth_group_permissions_permission_id` (`permission_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `django_content_type` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `app_label` varchar(100) NOT NULL,
            `model` varchar(100) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `django_content_type_app_label_model` (`app_label`,`model`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `django_admin_log` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `action_time` datetime(6) NOT NULL,
            `object_id` longtext,
            `object_repr` varchar(200) NOT NULL,
            `action_flag` smallint(5) unsigned NOT NULL,
            `change_message` longtext NOT NULL,
            `content_type_id` int(11) DEFAULT NULL,
            `user_id` int(11) NOT NULL,
            PRIMARY KEY (`id`),
            KEY `django_admin_log_content_type_id` (`content_type_id`),
            KEY `django_admin_log_user_id` (`user_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `django_migrations` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `app` varchar(255) NOT NULL,
            `name` varchar(255) NOT NULL,
            `applied` datetime(6) NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `django_session` (
            `session_key` varchar(40) NOT NULL,
            `session_data` longtext NOT NULL,
            `expire_date` datetime(6) NOT NULL,
            PRIMARY KEY (`session_key`),
            KEY `django_session_expire_date` (`expire_date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Добавляем записи в django_migrations для отметки миграций как примененных
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('contenttypes', '0001_initial', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('contenttypes', '0002_remove_content_type_name', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0001_initial', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0002_alter_permission_name_max_length', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0003_alter_user_email_max_length', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0004_alter_user_username_opts', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0005_alter_user_last_login_null', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0006_require_contenttypes_0002', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0007_alter_validators_add_error_messages', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0008_alter_user_username_max_length', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0009_alter_user_last_name_max_length', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0010_alter_group_name_max_length', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0011_update_proxy_permissions', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('auth', '0012_alter_user_first_name_max_length', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('admin', '0001_initial', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('admin', '0002_logentry_remove_auto_add', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('admin', '0003_logentry_add_action_flag_choices', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('sessions', '0001_initial', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('vacation', '0001_initial', NOW())")
        cursor.execute("INSERT IGNORE INTO django_migrations (app, name, applied) VALUES ('vacation', '0002_approvaldone_approvalfinal_approvalfirst_and_more', NOW())")
        
    conn.commit()
    print("Таблицы Django успешно созданы!")
    
except Exception as e:
    print(f"Ошибка: {e}")
    
finally:
    conn.close()
