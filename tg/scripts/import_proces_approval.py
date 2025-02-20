import pandas as pd
import pymysql
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import unidecode  # для преобразования румынских букв в латинские
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import engine  # Импортируем готовый engine из config.py

# Загрузка переменных окружения из корректного пути
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def create_db_connection():
    """Создание подключения к базе данных"""
    return engine  # Используем engine из config.py

def convert_to_latin(text):
    """Преобразование румынских букв в латинские"""
    if pd.isna(text):
        return None
    return unidecode.unidecode(str(text))

def clean_value(value):
    """Преобразование nan в None для MySQL и очистка пустых строк"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    return value

def check_tables_exist(engine):
    """Проверка существования необходимых таблиц"""
    with engine.connect() as connection:
        # Проверка таблицы name_dictionary
        result = connection.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name = 'name_dictionary'
        """, (engine.url.database,))
        if result.fetchone()[0] == 0:
            raise Exception("Таблица name_dictionary не существует")

        # Проверка таблицы approval_process
        result = connection.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_name = 'approval_process'
        """, (engine.url.database,))
        if result.fetchone()[0] == 0:
            raise Exception("Таблица approval_process не существует")

def update_name_dictionary(df, engine):
    """Обновление таблицы name_dictionary"""
    for _, row in df.iterrows():
        original_name = row['Nume/prenume']
        department = row['Secția']
        if pd.isna(original_name) or pd.isna(department):
            continue

        latin_name = convert_to_latin(original_name)
        
        with engine.connect() as connection:
            # Проверяем существование записи
            result = connection.execute("""
                SELECT id FROM name_dictionary 
                WHERE original_name = %s
            """, (original_name,))
            existing_record = result.fetchone()

            if existing_record:
                # Обновляем существующую запись
                connection.execute("""
                    UPDATE name_dictionary 
                    SET latin_name = %s, department = %s
                    WHERE original_name = %s
                """, (latin_name, department, original_name))
            else:
                # Добавляем новую запись
                connection.execute("""
                    INSERT INTO name_dictionary (original_name, latin_name, department)
                    VALUES (%s, %s, %s)
                """, (original_name, latin_name, department))

def update_approval_process(df, engine):
    """Обновление таблицы approval_process"""
    for _, row in df.iterrows():
        original_name = row['Nume/prenume']
        if pd.isna(original_name):
            continue

        # Получаем employee_name из name_dictionary
        with engine.connect() as connection:
            result = connection.execute("""
                SELECT latin_name FROM name_dictionary 
                WHERE original_name = %s
            """, (original_name,))
            record = result.fetchone()
            if not record:
                print(f"Предупреждение: Не найдено соответствие в name_dictionary для {original_name}")
                continue
            
            employee_name = record[0]

            # Подготовка данных для approval_process с обработкой nan
            data = {
                'original_name': clean_value(original_name),
                'employee_name': clean_value(employee_name),
                'first_approval': clean_value(row.get('I-a подпись')),
                'second_approval': clean_value(row.get('2-а подпись')),
                'final_approval': clean_value(row.get('Финальное решение')),
                'reception_info': clean_value(row.get('Инфо для рецепции')),
                'replacement': clean_value(row.get('Замена')),
                'timekeeper': clean_value(row.get('табельщик'))
            }

            # Проверяем существование записи
            result = connection.execute("""
                SELECT id FROM approval_process 
                WHERE original_name = %s
            """, (data['original_name'],))
            existing_record = result.fetchone()

            if existing_record:
                # Обновляем существующую запись
                query = """
                    UPDATE approval_process 
                    SET employee_name = %s, first_approval = %s, 
                        second_approval = %s, final_approval = %s,
                        reception_info = %s, replacement = %s, 
                        timekeeper = %s
                    WHERE original_name = %s
                """
                connection.execute(query, (
                    data['employee_name'], data['first_approval'],
                    data['second_approval'], data['final_approval'],
                    data['reception_info'], data['replacement'],
                    data['timekeeper'], data['original_name']
                ))
            else:
                # Добавляем новую запись
                query = """
                    INSERT INTO approval_process (
                        original_name, employee_name, first_approval,
                        second_approval, final_approval, reception_info,
                        replacement, timekeeper
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                connection.execute(query, (
                    data['original_name'], data['employee_name'],
                    data['first_approval'], data['second_approval'],
                    data['final_approval'], data['reception_info'],
                    data['replacement'], data['timekeeper']
                ))

def main(excel_file_path):
    """Основная функция импорта данных"""
    try:
        # Создаем подключение к БД
        engine = create_db_connection()
        
        # Проверяем существование таблиц
        check_tables_exist(engine)
        
        # Читаем Excel файл
        df = pd.read_excel(excel_file_path)
        
        # Обновляем таблицы
        update_name_dictionary(df, engine)
        update_approval_process(df, engine)
        
        print("Импорт данных успешно завершен")
        
    except Exception as e:
        print(f"Ошибка при импорте данных: {str(e)}")

if __name__ == "__main__":
    excel_file_path = r"C:\Users\User\Desktop\Список для процесса отпусков.xlsx"
    main(excel_file_path)