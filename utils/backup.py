import sqlite3
import shutil
import os
import json
from datetime import datetime
import zipfile
import hashlib

class DatabaseBackup:
    """Класс для резервного копирования базы данных"""
    
    @staticmethod
    def create_backup(db_path='repair_service.db', backup_dir='data/backups'):
        """Создание резервной копии БД"""
        try:
            # Создание директории для бэкапов
            os.makedirs(backup_dir, exist_ok=True)
            
            # Генерация имени файла с timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'backup_{timestamp}.db')
            
            # Копирование файла БД
            shutil.copy2(db_path, backup_file)
            
            # Создание файла с метаданными
            metadata = {
                'timestamp': timestamp,
                'database': db_path,
                'backup_file': backup_file,
                'size': os.path.getsize(backup_file),
                'checksum': DatabaseBackup._calculate_checksum(backup_file)
            }
            
            metadata_file = backup_file.replace('.db', '.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Очистка старых бэкапов (оставляем 10 последних)
            DatabaseBackup._cleanup_old_backups(backup_dir, keep_count=10)
            
            print(f"Резервная копия создана: {backup_file}")
            return backup_file
            
        except Exception as e:
            print(f"Ошибка при создании резервной копии: {e}")
            return None
    
    @staticmethod
    def create_zip_backup(db_path='repair_service.db', backup_dir='data/backups'):
        """Создание zip-архива с резервной копией"""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_file = os.path.join(backup_dir, f'backup_{timestamp}.zip')
            
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Добавление файла БД
                zipf.write(db_path, os.path.basename(db_path))
                
                # Добавление файлов конфигурации
                config_files = ['config.json', 'settings.ini']
                for config_file in config_files:
                    if os.path.exists(config_file):
                        zipf.write(config_file, config_file)
                
                # Добавление логов
                if os.path.exists('logs'):
                    for root, dirs, files in os.walk('logs'):
                        for file in files:
                            if file.endswith('.log'):
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, '.')
                                zipf.write(file_path, arcname)
            
            # Создание файла с метаданными
            metadata = {
                'timestamp': timestamp,
                'database': db_path,
                'backup_file': zip_file,
                'size': os.path.getsize(zip_file),
                'checksum': DatabaseBackup._calculate_checksum(zip_file),
                'type': 'zip'
            }
            
            metadata_file = zip_file.replace('.zip', '.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            DatabaseBackup._cleanup_old_backups(backup_dir, keep_count=10, extension='.zip')
            
            print(f"ZIP архив создан: {zip_file}")
            return zip_file
            
        except Exception as e:
            print(f"Ошибка при создании ZIP архива: {e}")
            return None
    
    @staticmethod
    def restore_backup(backup_file, db_path='repair_service.db'):
        """Восстановление БД из резервной копии"""
        try:
            # Проверка существования файла бэкапа
            if not os.path.exists(backup_file):
                print(f"Файл бэкапа не найден: {backup_file}")
                return False
            
            # Проверка контрольной суммы
            expected_checksum = None
            metadata_file = backup_file.replace('.db', '.json').replace('.zip', '.json')
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    expected_checksum = metadata.get('checksum')
            
            if expected_checksum:
                actual_checksum = DatabaseBackup._calculate_checksum(backup_file)
                if actual_checksum != expected_checksum:
                    print("Ошибка контрольной суммы файла бэкапа!")
                    return False
            
            # Создание резервной копии текущей БД
            if os.path.exists(db_path):
                temp_backup = db_path + '.temp'
                shutil.copy2(db_path, temp_backup)
            
            # Восстановление из обычного файла БД
            if backup_file.endswith('.db'):
                shutil.copy2(backup_file, db_path)
            
            # Восстановление из ZIP архива
            elif backup_file.endswith('.zip'):
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Поиск файла БД в архиве
                    db_files = [f for f in zipf.namelist() if f.endswith('.db')]
                    if db_files:
                        zipf.extract(db_files[0], os.path.dirname(db_path))
                        extracted_db = os.path.join(os.path.dirname(db_path), db_files[0])
                        shutil.move(extracted_db, db_path)
                    else:
                        print("Файл БД не найден в архиве")
                        return False
            
            else:
                print("Неизвестный формат файла бэкапа")
                return False
            
            print(f"БД успешно восстановлена из: {backup_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка при восстановлении БД: {e}")
            
            # Восстановление из временной копии
            temp_backup = db_path + '.temp'
            if os.path.exists(temp_backup):
                try:
                    shutil.copy2(temp_backup, db_path)
                    print("Восстановлена исходная БД из временной копии")
                except:
                    pass
            
            return False
    
    @staticmethod
    def export_to_sql(db_path='repair_service.db', export_dir='data/export'):
        """Экспорт БД в SQL файл"""
        try:
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sql_file = os.path.join(export_dir, f'database_{timestamp}.sql')
            
            conn = sqlite3.connect(db_path)
            
            with open(sql_file, 'w', encoding='utf-8') as f:
                # Экспорт схемы
                cursor = conn.cursor()
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
                
                for row in cursor.fetchall():
                    if row[0]:
                        f.write(f'{row[0]};\n\n')
                
                # Экспорт данных
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    # Пропускаем системные таблицы
                    if table.startswith('sqlite_'):
                        continue
                    
                    cursor.execute(f'SELECT * FROM {table}')
                    columns = [description[0] for description in cursor.description]
                    
                    f.write(f'-- Данные таблицы {table}\n')
                    
                    for row in cursor.fetchall():
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # Экранирование кавычек
                                value = value.replace("'", "''")
                                values.append(f"'{value}'")
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            else:
                                values.append(f"'{str(value)}'")
                        
                        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                        f.write(sql)
                    
                    f.write('\n')
            
            conn.close()
            
            print(f"БД экспортирована в SQL: {sql_file}")
            return sql_file
            
        except Exception as e:
            print(f"Ошибка при экспорте БД в SQL: {e}")
            return None
    
    @staticmethod
    def _calculate_checksum(file_path):
        """Расчет контрольной суммы файла"""
        hash_md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    @staticmethod
    def _cleanup_old_backups(backup_dir, keep_count=10, extension='.db'):
        """Очистка старых бэкапов"""
        try:
            # Поиск файлов бэкапов
            backup_files = []
            for file in os.listdir(backup_dir):
                if file.endswith(extension) and file.startswith('backup_'):
                    file_path = os.path.join(backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Сортировка по дате создания (новые первыми)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Удаление старых файлов
            for i in range(keep_count, len(backup_files)):
                file_path, _ = backup_files[i]
                
                try:
                    os.remove(file_path)
                    
                    # Удаление файла метаданных
                    metadata_file = file_path.replace(extension, '.json')
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)
                    
                    print(f"Удален старый бэкап: {file_path}")
                except Exception as e:
                    print(f"Ошибка при удалении файла {file_path}: {e}")
                    
        except Exception as e:
            print(f"Ошибка при очистке старых бэкапов: {e}")
    
    @staticmethod
    def list_backups(backup_dir='data/backups'):
        """Список доступных бэкапов"""
        try:
            backups = []
            
            if not os.path.exists(backup_dir):
                return backups
            
            for file in os.listdir(backup_dir):
                if file.endswith('.db') and file.startswith('backup_'):
                    file_path = os.path.join(backup_dir, file)
                    metadata_file = file_path.replace('.db', '.json')
                    
                    backup_info = {
                        'file': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                    }
                    
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    
                    backups.append(backup_info)
            
            # Сортировка по дате (новые первыми)
            backups.sort(key=lambda x: x.get('modified', datetime.min), reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"Ошибка при получении списка бэкапов: {e}")
            return []
    
    @staticmethod
    def verify_backup(backup_file):
        """Проверка целостности бэкапа"""
        try:
            if not os.path.exists(backup_file):
                return False, "Файл не найден"
            
            # Проверка контрольной суммы
            metadata_file = backup_file.replace('.db', '.json').replace('.zip', '.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    expected_checksum = metadata.get('checksum')
                    
                    if expected_checksum:
                        actual_checksum = DatabaseBackup._calculate_checksum(backup_file)
                        if actual_checksum != expected_checksum:
                            return False, "Неверная контрольная сумма"
            
            # Проверка структуры БД
            if backup_file.endswith('.db'):
                try:
                    conn = sqlite3.connect(backup_file)
                    cursor = conn.cursor()
                    
                    # Проверка наличия основных таблиц
                    required_tables = ['users', 'requests', 'comments']
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    existing_tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in required_tables:
                        if table not in existing_tables:
                            conn.close()
                            return False, f"Отсутствует таблица: {table}"
                    
                    conn.close()
                except sqlite3.Error as e:
                    return False, f"Ошибка БД: {e}"
            
            return True, "Бэкап целостен"
            
        except Exception as e:
            return False, f"Ошибка при проверке: {e}"
    
    @staticmethod
    def schedule_backup(cron_expression='0 2 * * *'):
        """Настройка автоматического резервного копирования"""
        # В реальном приложении здесь была бы интеграция с планировщиком задач
        # Для Windows: Task Scheduler
        # Для Linux: cron
        
        schedule_info = {
            'expression': cron_expression,
            'description': 'Автоматическое резервное копирование БД',
            'next_run': 'Ежедневно в 02:00'
        }
        
        print(f"Настроено автоматическое резервное копирование: {schedule_info}")
        return schedule_info