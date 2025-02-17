import mysql.connector
import pandas as pd
import unidecode

# Конфигурация подключения к БД
db_config = {
    'host': '192.168.101.90',
    'user': 'suceava15a',
    'password': 'Kiev73',
    'database': 'HR_db',
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Путь к Excel файлу
excel_file = r"C:\Users\User\Desktop\Список для процесса отпусков.xlsx"

def ensure_tables_exist(cursor):
    """Проверка существования таблиц и их создание при необходимости"""
    # Проверяем существование таблицы name_dictionary
    cursor.execute("SHOW TABLES LIKE 'name_dictionary'")
    if not cursor.fetchone():
        print("Создание таблицы name_dictionary...")
        create_name_dict_query = """
        CREATE TABLE name_dictionary (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_name VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            latin_name VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
            department VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            UNIQUE KEY unique_original_name (original_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_romanian_ci;
        """
        cursor.execute(create_name_dict_query)

    # Проверяем существование таблицы approval_process
    cursor.execute("SHOW TABLES LIKE 'approval_process'")
    if not cursor.fetchone():
        print("Создание таблицы approval_process...")
        create_approval_process_query = """
        CREATE TABLE approval_process (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_name VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            first_approval VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            second_approval VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            final_approval VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            reception_info ENUM('', 'da') DEFAULT '',
            replacement VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            timekeeper VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_romanian_ci,
            FOREIGN KEY (employee_name) REFERENCES name_dictionary(original_name),
            UNIQUE KEY unique_employee (employee_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_romanian_ci;
        """
        cursor.execute(create_approval_process_query)

def setup_database_connection():
    """Настройка соединения с базой данных"""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)  # Получаем результаты в виде словарей
    
    # Устанавливаем правильную кодировку для соединения
    cursor.execute('SET NAMES utf8mb4')
    cursor.execute('SET CHARACTER SET utf8mb4')
    cursor.execute('SET character_set_connection=utf8mb4')
    
    return conn, cursor

def sync_data_from_excel():
    try:
        # Чтение данных из Excel
        print("Чтение данных из Excel файла...")
        df = pd.read_excel(excel_file)
        
        # Подключение к БД
        print("Подключение к базе данных...")
        conn, cursor = setup_database_connection()
        
        # Проверяем существование таблиц
        ensure_tables_exist(cursor)
        
        # Счетчики изменений
        changes = {
            'names_added': 0,
            'names_updated': 0,
            'approvals_added': 0,
            'approvals_updated': 0
        }
        
        # Обновляем словарь имен
        print("\nСинхронизация словаря имен...")
        for _, row in df.iterrows():
            if pd.isna(row['Nume/prenume']) or pd.isna(row['Secția']):
                continue
                
            original_name = str(row['Nume/prenume']).strip()
            department = str(row['Secția']).strip()
            
            if not original_name or not department:
                continue
            
            latin_name = unidecode.unidecode(original_name)
            
            # Проверяем существование записи
            cursor.execute("SELECT * FROM name_dictionary WHERE original_name = %s", (original_name,))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Проверяем, нужно ли обновление
                if existing_record['department'] != department or existing_record['latin_name'] != latin_name:
                    cursor.execute("""
                        UPDATE name_dictionary 
                        SET latin_name = %s, department = %s 
                        WHERE original_name = %s
                    """, (latin_name, department, original_name))
                    changes['names_updated'] += 1
                    print(f"Обновлено имя: {original_name}")
            else:
                # Добавляем новую запись
                cursor.execute("""
                    INSERT INTO name_dictionary (original_name, latin_name, department)
                    VALUES (%s, %s, %s)
                """, (original_name, latin_name, department))
                changes['names_added'] += 1
                print(f"Добавлено новое имя: {original_name}")
        
        # Обновляем процессы утверждения
        print("\nСинхронизация процессов утверждения...")
        for _, row in df.iterrows():
            if pd.isna(row['Nume/prenume']):
                continue
                
            employee_name = str(row['Nume/prenume']).strip()
            
            # Получаем значения подписей, избегая дубликатов
            approvers = []
            for field in ['I-a подпись', '2-а подпись', 'Финальное решение']:
                if pd.notna(row[field]):
                    approver = str(row[field]).strip()
                    if approver and approver not in approvers:
                        approvers.append(approver)
            
            # Заполняем подписи
            first_approval = approvers[0] if len(approvers) > 0 else None
            second_approval = approvers[1] if len(approvers) > 1 else None
            final_approval = approvers[2] if len(approvers) > 2 else None
            
            # Получаем остальные данные
            reception_info = 'da' if pd.notna(row['Инфо для рецепции']) and str(row['Инфо для рецепции']).strip().lower() == 'da' else ''
            replacement = str(row['Замена']).strip() if pd.notna(row['Замена']) else None
            timekeeper = str(row['табельщик']).strip() if pd.notna(row['табельщик']) else None
            
            # Проверяем существование записи
            cursor.execute("SELECT * FROM approval_process WHERE employee_name = %s", (employee_name,))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Проверяем, нужно ли обновление
                if (existing_record['first_approval'] != first_approval or
                    existing_record['second_approval'] != second_approval or
                    existing_record['final_approval'] != final_approval or
                    existing_record['reception_info'] != reception_info or
                    existing_record['replacement'] != replacement or
                    existing_record['timekeeper'] != timekeeper):
                    
                    cursor.execute("""
                        UPDATE approval_process 
                        SET first_approval = %s, second_approval = %s, final_approval = %s,
                            reception_info = %s, replacement = %s, timekeeper = %s
                        WHERE employee_name = %s
                    """, (first_approval, second_approval, final_approval,
                          reception_info, replacement, timekeeper, employee_name))
                    changes['approvals_updated'] += 1
                    print(f"Обновлен процесс утверждения для: {employee_name}")
            else:
                # Добавляем новую запись
                try:
                    cursor.execute("""
                        INSERT INTO approval_process 
                        (employee_name, first_approval, second_approval, final_approval,
                         reception_info, replacement, timekeeper)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (employee_name, first_approval, second_approval, final_approval,
                          reception_info, replacement, timekeeper))
                    changes['approvals_added'] += 1
                    print(f"Добавлен новый процесс утверждения для: {employee_name}")
                except mysql.connector.Error as err:
                    print(f"Ошибка при добавлении процесса утверждения для {employee_name}: {err}")
        
        # Сохраняем изменения
        conn.commit()
        
        # Выводим статистику изменений
        print("\nСтатистика изменений:")
        print(f"Добавлено новых имен: {changes['names_added']}")
        print(f"Обновлено имен: {changes['names_updated']}")
        print(f"Добавлено новых процессов утверждения: {changes['approvals_added']}")
        print(f"Обновлено процессов утверждения: {changes['approvals_updated']}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nСоединение с базой данных закрыто")

if __name__ == '__main__':
    sync_data_from_excel()