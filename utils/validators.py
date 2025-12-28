import re
from datetime import datetime

class Validators:
    """Класс для валидации данных"""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация номера телефона"""
        # Российские номера: +7XXXXXXXXXX или 8XXXXXXXXXX
        pattern = r'^(\+7|8)[0-9]{10}$'
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Валидация даты"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_russian_name(name: str) -> bool:
        """Валидация русского имени"""
        pattern = r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_price(price: str) -> bool:
        """Валидация цены"""
        try:
            value = float(price)
            return value >= 0
        except ValueError:
            return False
    
    @staticmethod
    def validate_integer(value: str, min_val: int = None, max_val: int = None) -> bool:
        """Валидация целого числа"""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_text_length(text: str, min_len: int = 0, max_len: int = None) -> bool:
        """Валидация длины текста"""
        length = len(text.strip())
        if length < min_len:
            return False
        if max_len is not None and length > max_len:
            return False
        return True
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Санитизация ввода (защита от SQL-инъекций и XSS)"""
        # Удаление потенциально опасных символов
        sanitized = re.sub(r'[<>"\';]', '', text)
        return sanitized.strip()
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Валидация пароля"""
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"
        
        if not re.search(r'[A-ZА-Я]', password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"
        
        if not re.search(r'[a-zа-я]', password):
            return False, "Пароль должен содержать хотя бы одну строчную букву"
        
        if not re.search(r'\d', password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
            return False, "Пароль должен содержать хотя бы один специальный символ"
        
        return True, "Пароль валиден"
    
    @staticmethod
    def validate_vendor_code(code: str) -> bool:
        """Валидация артикула"""
        pattern = r'^[A-Z0-9\-_]{3,20}$'
        return bool(re.match(pattern, code))
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Форматирование телефона"""
        cleaned = re.sub(r'[^\d]', '', phone)
        
        if cleaned.startswith('8'):
            cleaned = '7' + cleaned[1:]
        elif not cleaned.startswith('7'):
            cleaned = '7' + cleaned
        
        if len(cleaned) == 11:
            return f"+{cleaned[0]} ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:]}"
        
        return phone