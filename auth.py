import hashlib
import secrets
from datetime import datetime, timedelta
from database import Database
from models import User

class AuthSystem:
    """Система аутентификации"""
    
    def __init__(self):
        self.db = Database()
        self.current_user = None
        self.session_token = None
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = secrets.token_hex(16)
        return f"{salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        try:
            salt, hash_value = hashed_password.split('$')
            return hashlib.sha256((salt + plain_password).encode()).hexdigest() == hash_value
        except:
            return False
    
    def create_access_token(self, data: dict) -> str:
        """Создание простого токена сессии"""
        import json
        import base64
        import time
        
        data['timestamp'] = time.time()
        token_data = json.dumps(data).encode()
        return base64.b64encode(token_data).decode()
    
    def verify_token(self, token: str) -> dict:
        """Проверка токена сессии"""
        try:
            import json
            import base64
            import time
            
            token_data = base64.b64decode(token).decode()
            data = json.loads(token_data)
            
            # Проверка времени жизни токена (24 часа)
            if time.time() - data.get('timestamp', 0) > 86400:
                return None
            
            return data
        except:
            return None
    
    def login(self, login: str, password: str, remember_me: bool = False) -> bool:
        """Авторизация пользователя"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE login = ? AND is_active = 1
            ''', (login,))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # В демо-режиме используем простую проверку
                if user_data['password'] == password:  # Для демо
                # Для продакшена: if self.verify_password(password, user_data['password']):
                    self.current_user = User(**user_data)
                    
                    # Создание простого токена сессии
                    token_data = {
                        "user_id": self.current_user.userID,
                        "login": self.current_user.login,
                        "type": self.current_user.type
                    }
                    
                    self.session_token = self.create_access_token(token_data)
                    
                    # Запись в лог
                    self.log_login_attempt(login, True)
                    return True
                
                self.log_login_attempt(login, False)
        
        return False
    
    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.session_token = None
    
    def is_authenticated(self) -> bool:
        """Проверка аутентификации"""
        return self.current_user is not None
    
    def get_current_user(self) -> User:
        """Получить текущего пользователя"""
        return self.current_user
    
    def has_permission(self, permission: str) -> bool:
        """Проверка разрешений"""
        if not self.current_user:
            return False
        
        return self.current_user.has_permission(permission)
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """Смена пароля"""
        if not self.current_user:
            return False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверка старого пароля
            cursor.execute('SELECT password FROM users WHERE userID = ?', 
                         (self.current_user.userID,))
            stored_password = cursor.fetchone()['password']
            
            if stored_password != old_password:  # Для демо
            # Для продакшена: if not self.verify_password(old_password, stored_password):
                return False
            
            # Обновление пароля
            # hashed_password = self.hash_password(new_password)  # Для продакшена
            cursor.execute('''
                UPDATE users 
                SET password = ?
                WHERE userID = ?
            ''', (new_password, self.current_user.userID))
            
            conn.commit()
            
            # Обновление объекта пользователя
            self.current_user.password = new_password
            
            return True
    
    def register_user(self, fio: str, phone: str, login: str, 
                     password: str, user_type: str) -> bool:
        """Регистрация нового пользователя"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверка существования логина
            cursor.execute('SELECT COUNT(*) FROM users WHERE login = ?', (login,))
            if cursor.fetchone()[0] > 0:
                return False
            
            # Хеширование пароля
            # hashed_password = self.hash_password(password)  # Для продакшена
            
            try:
                cursor.execute('''
                    INSERT INTO users (fio, phone, login, password, type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (fio, phone, login, password, user_type))
                
                conn.commit()
                return True
            except:
                return False
    
    def update_user_profile(self, fio: str = None, phone: str = None) -> bool:
        """Обновление профиля пользователя"""
        if not self.current_user:
            return False
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if fio:
                updates.append("fio = ?")
                params.append(fio)
                self.current_user.fio = fio
            
            if phone:
                updates.append("phone = ?")
                params.append(phone)
                self.current_user.phone = phone
            
            if not updates:
                return True
            
            params.append(self.current_user.userID)
            
            query = f'''
                UPDATE users 
                SET {', '.join(updates)}
                WHERE userID = ?
            '''
            
            cursor.execute(query, params)
            conn.commit()
            
            return True
    
    def log_login_attempt(self, login: str, success: bool):
        """Логирование попытки входа"""
        try:
            with open('logs/auth.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status = "SUCCESS" if success else "FAILED"
                f.write(f"{timestamp} - {login} - {status}\n")
        except:
            pass
    
    def get_login_history(self, limit=50):
        """Получение истории входов"""
        try:
            with open('logs/auth.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()[-limit:]
                return [line.strip() for line in reversed(lines)]
        except:
            return []
    
    def validate_session(self, token: str) -> bool:
        """Валидация сессии по токену"""
        payload = self.verify_token(token)
        
        if not payload:
            return False
        
        # Восстановление пользователя из токена
        user_id = payload.get("user_id")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE userID = ?', (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                self.current_user = User(**user_data)
                self.session_token = token
                return True
        
        return False