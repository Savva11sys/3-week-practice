import sqlite3
import csv
import os
from datetime import datetime
import json

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_name='repair_service.db'):
        self.db_name = db_name
        self.init_database()
        self.create_demo_data()
    
    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Инициализация базы данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    userID INTEGER PRIMARY KEY AUTOINCREMENT,
                    fio TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    login TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('Менеджер', 'Мастер', 'Оператор', 'Заказчик', 'Менеджер качества')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Таблица заявок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    requestID INTEGER PRIMARY KEY AUTOINCREMENT,
                    startDate DATE NOT NULL,
                    homeTechType TEXT NOT NULL,
                    homeTechModel TEXT NOT NULL,
                    problemDescription TEXT NOT NULL,
                    requestStatus TEXT NOT NULL CHECK(requestStatus IN ('Новая заявка', 'В процессе ремонта', 'Ожидание запчастей', 'Готова к выдаче')),
                    completionDate DATE,
                    repairParts TEXT,
                    masterID INTEGER,
                    clientID INTEGER NOT NULL,
                    qualityManagerID INTEGER,
                    extendedDeadline DATE,
                    estimatedCost REAL DEFAULT 0,
                    actualCost REAL DEFAULT 0,
                    priority INTEGER DEFAULT 1 CHECK(priority BETWEEN 1 AND 5),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (masterID) REFERENCES users(userID) ON DELETE SET NULL,
                    FOREIGN KEY (clientID) REFERENCES users(userID) ON DELETE CASCADE,
                    FOREIGN KEY (qualityManagerID) REFERENCES users(userID) ON DELETE SET NULL
                )
            ''')
            
            # Таблица комментариев
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    commentID INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    masterID INTEGER NOT NULL,
                    requestID INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_private INTEGER DEFAULT 0,
                    FOREIGN KEY (masterID) REFERENCES users(userID) ON DELETE CASCADE,
                    FOREIGN KEY (requestID) REFERENCES requests(requestID) ON DELETE CASCADE
                )
            ''')
            
            # Таблица статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    statID INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_requests INTEGER DEFAULT 0,
                    completed_requests INTEGER DEFAULT 0,
                    avg_repair_time REAL DEFAULT 0,
                    total_revenue REAL DEFAULT 0,
                    UNIQUE(date)
                )
            ''')
            
            # Таблица запчастей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parts (
                    partID INTEGER PRIMARY KEY AUTOINCREMENT,
                    partName TEXT NOT NULL,
                    vendorCode TEXT UNIQUE,
                    price REAL,
                    quantity INTEGER DEFAULT 0,
                    min_quantity INTEGER DEFAULT 5,
                    supplier TEXT,
                    last_ordered DATE
                )
            ''')
            
            # Таблица связей запчастей и заявок
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_parts (
                    requestID INTEGER NOT NULL,
                    partID INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    used_date DATE DEFAULT CURRENT_DATE,
                    PRIMARY KEY (requestID, partID),
                    FOREIGN KEY (requestID) REFERENCES requests(requestID) ON DELETE CASCADE,
                    FOREIGN KEY (partID) REFERENCES parts(partID) ON DELETE CASCADE
                )
            ''')
            
            # Таблица уведомлений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    notificationID INTEGER PRIMARY KEY AUTOINCREMENT,
                    userID INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE
                )
            ''')
            
            # Индексы для оптимизации
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(requestStatus)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_master ON requests(masterID)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_client ON requests(clientID)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_request ON comments(requestID)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_type ON users(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_requests_priority ON requests(priority)')
            
            # Триггер для обновления updated_at
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_requests_timestamp 
                AFTER UPDATE ON requests
                BEGIN
                    UPDATE requests SET updated_at = CURRENT_TIMESTAMP WHERE requestID = NEW.requestID;
                END;
            ''')
            
            conn.commit()
    
    def create_demo_data(self):
        """Создание демо-данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем есть ли пользователи
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                print("Создание демо-данных...")
                
                # Демо-пользователи
                demo_users = [
                    ('Трубин Никита Юрьевич', '89210563128', 'kasoo', 'root', 'Менеджер'),
                    ('Мурашов Андрей Юрьевич', '89535078985', 'murashov123', 'qwerty', 'Мастер'),
                    ('Степанов Андрей Викторович', '89210673849', 'test1', 'test1', 'Мастер'),
                    ('Перина Анастасия Денисовна', '89990563748', 'perinaAD', '250519', 'Оператор'),
                    ('Мажитова Ксения Сергеевна', '89994563847', 'krutiha', '123456', 'Оператор'),
                    ('Семенова Ясмина Марковна', '89994563847', 'login1', 'pass1', 'Мастер'),
                    ('Баранова Эмилия Марковна', '89994563841', 'client1', 'pass1', 'Заказчик'),
                    ('Егорова Алиса Платоновна', '89994563842', 'client2', 'pass2', 'Заказчик'),
                    ('Титов Максим Иванович', '89994563843', 'client3', 'pass3', 'Заказчик'),
                    ('Иванов Марк Максимович', '89994563844', 'quality', 'quality123', 'Менеджер качества')
                ]
                
                for user in demo_users:
                    cursor.execute('''
                        INSERT OR IGNORE INTO users (fio, phone, login, password, type)
                        VALUES (?, ?, ?, ?, ?)
                    ''', user)
                
                # Демо-заявки
                demo_requests = [
                    ('2023-06-06', 'Фен', 'Ладомир ТА112 белый', 'Перестал работать', 'В процессе ремонта', None, '', 2, 7, None, None, 1500, 0, 2, ''),
                    ('2023-05-05', 'Тостер', 'Redmond RT-437 черный', 'Перестал работать', 'В процессе ремонта', None, '', 3, 7, None, None, 2000, 0, 3, ''),
                    ('2022-07-07', 'Холодильник', 'Indesit DS 316 W белый', 'Не морозит одна из камер', 'Готова к выдаче', '2023-01-01', '', 2, 8, None, None, 5000, 4500, 1, ''),
                    ('2023-08-02', 'Стиральная машина', 'DEXP WM-F610NTMA/WW белый', 'Перестали работать режимы стирки', 'Новая заявка', None, '', None, 8, None, None, 3000, 0, 2, ''),
                    ('2023-08-02', 'Мультиварка', 'Redmond RMC-M95 черный', 'Перестала включаться', 'Ожидание запчастей', None, 'Блок питания', None, 9, 10, None, 2500, 0, 4, 'Ждет доставки запчастей'),
                    ('2023-08-02', 'Фен', 'Ладомир ТА113 чёрный', 'Перестал работать', 'Готова к выдаче', '2023-08-03', '', 2, 7, None, None, 1200, 1100, 3, ''),
                    ('2023-07-09', 'Холодильник', 'Indesit DS 314 W серый', 'Гудит, но не замораживает', 'Готова к выдаче', '2023-08-03', 'Мотор обдува', 2, 8, None, None, 6000, 5500, 1, 'Замена мотора')
                ]
                
                for req in demo_requests:
                    cursor.execute('''
                        INSERT INTO requests 
                        (startDate, homeTechType, homeTechModel, problemDescription, 
                         requestStatus, completionDate, repairParts, masterID, clientID, 
                         qualityManagerID, extendedDeadline, estimatedCost, actualCost, 
                         priority, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', req)
                
                # Демо-комментарии
                demo_comments = [
                    ('Интересная поломка, нужно разобрать и проверить', 2, 1, 0),
                    ('Очень странно, будем разбираться!', 3, 2, 0),
                    ('Скорее всего потребуется мотор обдува! Заказали', 2, 7, 0),
                    ('Клиент просит ускорить ремонт', 2, 1, 1),
                    ('Очень странно, будем разбираться!', 3, 6, 0),
                    ('Ремонт завершен, можно выдавать', 2, 3, 0)
                ]
                
                for comment in demo_comments:
                    cursor.execute('''
                        INSERT INTO comments (message, masterID, requestID, is_private)
                        VALUES (?, ?, ?, ?)
                    ''', comment)
                
                # Демо-запчасти
                demo_parts = [
                    ('Мотор обдува холодильника', 'MOT-IND-001', 1500.00, 3, 2, 'Indesit', '2023-07-15'),
                    ('Блок питания мультиварки', 'PS-RED-001', 800.00, 0, 5, 'Redmond', '2023-07-20'),
                    ('Тэн стиральной машины', 'TEN-DEXP-001', 1200.00, 5, 3, 'DEXP', '2023-07-10'),
                    ('Вентилятор фена', 'FAN-LAD-001', 300.00, 10, 5, 'Ладомир', '2023-07-05'),
                    ('Плата управления тостера', 'PCB-RED-001', 900.00, 2, 3, 'Redmond', '2023-07-18')
                ]
                
                for part in demo_parts:
                    cursor.execute('''
                        INSERT INTO parts (partName, vendorCode, price, quantity, min_quantity, supplier, last_ordered)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', part)
                
                conn.commit()
                print("Демо-данные созданы успешно!")
    
    def get_statistics(self):
        """Получение статистики"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Общая статистика
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN requestStatus != 'Готова к выдаче' THEN 1 ELSE 0 END) as active_requests,
                    SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed_requests,
                    AVG(CASE WHEN completionDate IS NOT NULL 
                        THEN julianday(completionDate) - julianday(startDate) 
                        ELSE NULL END) as avg_repair_days,
                    SUM(actualCost) as total_revenue,
                    COUNT(DISTINCT clientID) as unique_clients
                FROM requests
            ''')
            
            stats = dict(cursor.fetchone())
            
            # Статистика по статусам
            cursor.execute('''
                SELECT requestStatus, COUNT(*) as count
                FROM requests 
                GROUP BY requestStatus
                ORDER BY count DESC
            ''')
            
            stats['by_status'] = dict(cursor.fetchall())
            
            # Статистика по типам техники
            cursor.execute('''
                SELECT homeTechType, COUNT(*) as count,
                       AVG(CASE WHEN completionDate IS NOT NULL 
                           THEN julianday(completionDate) - julianday(startDate) 
                           ELSE NULL END) as avg_days
                FROM requests 
                GROUP BY homeTechType
                ORDER BY count DESC
            ''')
            
            stats['by_tech_type'] = cursor.fetchall()
            
            # Статистика по мастерам
            cursor.execute('''
                SELECT u.fio, COUNT(r.requestID) as total,
                       SUM(CASE WHEN r.requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                       AVG(CASE WHEN r.completionDate IS NOT NULL 
                           THEN julianday(r.completionDate) - julianday(r.startDate) 
                           ELSE NULL END) as avg_days
                FROM users u
                LEFT JOIN requests r ON u.userID = r.masterID
                WHERE u.type = 'Мастер'
                GROUP BY u.userID
                ORDER BY completed DESC
            ''')
            
            stats['by_master'] = cursor.fetchall()
            
            # Статистика по месяцам
            cursor.execute('''
                SELECT strftime('%Y-%m', startDate) as month,
                       COUNT(*) as count,
                       SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed
                FROM requests
                GROUP BY strftime('%Y-%m', startDate)
                ORDER BY month DESC
                LIMIT 6
            ''')
            
            stats['by_month'] = cursor.fetchall()
            
            return stats
    
    def get_user_requests(self, user_id, user_type):
        """Получение заявок пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_type == 'Мастер':
                query = '''
                    SELECT r.*, c.fio as client_name, c.phone as client_phone
                    FROM requests r
                    JOIN users c ON r.clientID = c.userID
                    WHERE r.masterID = ?
                    ORDER BY r.priority DESC, r.startDate DESC
                '''
                params = (user_id,)
            elif user_type == 'Заказчик':
                query = '''
                    SELECT r.*, m.fio as master_name
                    FROM requests r
                    LEFT JOIN users m ON r.masterID = m.userID
                    WHERE r.clientID = ?
                    ORDER BY r.startDate DESC
                '''
                params = (user_id,)
            else:
                query = '''
                    SELECT r.*, c.fio as client_name, m.fio as master_name
                    FROM requests r
                    LEFT JOIN users c ON r.clientID = c.userID
                    LEFT JOIN users m ON r.masterID = m.userID
                    ORDER BY r.startDate DESC
                '''
                params = ()
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def search_requests(self, search_term, filters=None):
        """Поиск заявок с фильтрами"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT r.*, c.fio as client_name, m.fio as master_name
                FROM requests r
                LEFT JOIN users c ON r.clientID = c.userID
                LEFT JOIN users m ON r.masterID = m.userID
                WHERE 1=1
            '''
            
            params = []
            
            # Поиск по тексту
            if search_term:
                query += '''
                    AND (r.requestID LIKE ? OR 
                         r.homeTechType LIKE ? OR 
                         r.homeTechModel LIKE ? OR 
                         r.problemDescription LIKE ? OR
                         c.fio LIKE ? OR
                         m.fio LIKE ?)
                '''
                search_param = f"%{search_term}%"
                params.extend([search_param] * 6)
            
            # Применение фильтров
            if filters:
                if filters.get('status'):
                    query += " AND r.requestStatus = ?"
                    params.append(filters['status'])
                
                if filters.get('tech_type'):
                    query += " AND r.homeTechType = ?"
                    params.append(filters['tech_type'])
                
                if filters.get('master_id'):
                    query += " AND r.masterID = ?"
                    params.append(filters['master_id'])
                
                if filters.get('priority'):
                    query += " AND r.priority = ?"
                    params.append(filters['priority'])
                
                if filters.get('date_from'):
                    query += " AND r.startDate >= ?"
                    params.append(filters['date_from'])
                
                if filters.get('date_to'):
                    query += " AND r.startDate <= ?"
                    params.append(filters['date_to'])
            
            query += " ORDER BY r.priority DESC, r.startDate DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_request_status(self, request_id, status, completion_date=None):
        """Обновление статуса заявки"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status == 'Готова к выдаче' and not completion_date:
                completion_date = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
                UPDATE requests 
                SET requestStatus = ?, 
                    completionDate = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE requestID = ?
            ''', (status, completion_date, request_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def add_notification(self, user_id, message, notification_type='info'):
        """Добавление уведомления"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (userID, message, type)
                VALUES (?, ?, ?)
            ''', (user_id, message, notification_type))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_user_notifications(self, user_id, unread_only=False):
        """Получение уведомлений пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM notifications 
                WHERE userID = ?
            '''
            
            if unread_only:
                query += " AND is_read = 0"
            
            query += " ORDER BY created_at DESC LIMIT 50"
            
            cursor.execute(query, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_notification_read(self, notification_id):
        """Пометить уведомление как прочитанное"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1 
                WHERE notificationID = ?
            ''', (notification_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_low_stock_parts(self):
        """Получение запчастей с низким запасом"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM parts 
                WHERE quantity <= min_quantity
                ORDER BY quantity ASC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_overdue_requests(self, days_threshold=7):
        """Получение просроченных заявок"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, c.fio as client_name, m.fio as master_name,
                       julianday('now') - julianday(r.startDate) as days_passed
                FROM requests r
                LEFT JOIN users c ON r.clientID = c.userID
                LEFT JOIN users m ON r.masterID = m.userID
                WHERE r.requestStatus != 'Готова к выдаче'
                AND julianday('now') - julianday(r.startDate) > ?
                ORDER BY days_passed DESC
            ''', (days_threshold,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_data(self, table_name, format='json'):
        """Экспорт данных таблицы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f'SELECT * FROM {table_name}')
            data = [dict(row) for row in cursor.fetchall()]
            
            if format == 'json':
                return json.dumps(data, ensure_ascii=False, indent=2, default=str)
            elif format == 'csv':
                import io
                import csv as csv_module
                
                output = io.StringIO()
                if data:
                    writer = csv_module.DictWriter(output, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                return output.getvalue()
            
            return data