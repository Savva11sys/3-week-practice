import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import random
import string

class QRCodeGenerator:
    """Генератор QR-кодов"""
    
    @staticmethod
    def generate_feedback_qr(request_id: int, customer_name: str = "") -> str:
        """Генерация QR-кода для оценки качества"""
        feedback_url = f"https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=pp_url&entry.123456789={request_id}"
        
        # Создание QR-кода
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(feedback_url)
        qr.make(fit=True)
        
        # Создание изображения
        img = qr.make_image(fill_color="#2c3e50", back_color="white")
        
        # Добавление текста
        draw = ImageDraw.Draw(img)
        
        try:
            # Использование стандартного шрифта
            font = ImageFont.load_default()
            
            # Текст
            text = f"Заявка #{request_id}"
            if customer_name:
                text += f"\n{customer_name}"
            
            text += "\nОцените качество работы"
            
            # Расчет позиции
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[0]
            
            # Позиционирование текста
            img_width, img_height = img.size
            x = (img_width - text_width) // 2
            y = img_height - text_height - 10
            
            # Рисование текста
            draw.text((x, y), text, fill="#2c3e50", font=font)
        except:
            pass  # Если не удалось добавить текст, оставляем просто QR-код
        
        # Сохранение файла
        os.makedirs("data/export/qr_codes", exist_ok=True)
        filename = f"data/export/qr_codes/qr_request_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        
        return filename
    
    @staticmethod
    def generate_receipt_qr(request_id: int, amount: float) -> str:
        """Генерация QR-кода для оплаты"""
        # Здесь можно интегрировать с платежными системами
        payment_url = f"payment://request/{request_id}/amount/{amount}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#27ae60", back_color="white")
        
        os.makedirs("data/export/payments", exist_ok=True)
        filename = f"data/export/payments/payment_{request_id}.png"
        img.save(filename)
        
        return filename
    
    @staticmethod
    def generate_warranty_qr(request_id: int, warranty_months: int) -> str:
        """Генерация QR-кода гарантийного талона"""
        warranty_data = {
            'request_id': request_id,
            'issue_date': datetime.now().strftime("%Y-%m-%d"),
            'warranty_months': warranty_months,
            'expiry_date': (datetime.now() + datetime.timedelta(days=warranty_months*30)).strftime("%Y-%m-%d")
        }
        
        import json
        data_str = json.dumps(warranty_data)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_str)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#3498db", back_color="white")
        
        os.makedirs("data/export/warranty", exist_ok=True)
        filename = f"data/export/warranty/warranty_{request_id}.png"
        img.save(filename)
        
        return filename

class ReportGenerator:
    """Генератор отчетов"""
    
    @staticmethod
    def generate_daily_report(db_connection, date=None):
        """Генерация ежедневного отчета"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Статистика за день
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                    SUM(actualCost) as revenue,
                    COUNT(DISTINCT clientID) as unique_clients
                FROM requests 
                WHERE DATE(startDate) = ?
            ''', (date,))
            
            stats = cursor.fetchone()
            
            # Новые заявки
            cursor.execute('''
                SELECT r.requestID, r.homeTechType, r.problemDescription, 
                       u.fio as client_name, m.fio as master_name
                FROM requests r
                LEFT JOIN users u ON r.clientID = u.userID
                LEFT JOIN users m ON r.masterID = m.userID
                WHERE DATE(r.startDate) = ?
                ORDER BY r.requestID
            ''', (date,))
            
            new_requests = cursor.fetchall()
            
            # Завершенные заявки
            cursor.execute('''
                SELECT r.requestID, r.homeTechType, r.actualCost,
                       u.fio as client_name, m.fio as master_name
                FROM requests r
                LEFT JOIN users u ON r.clientID = u.userID
                LEFT JOIN users m ON r.masterID = m.userID
                WHERE DATE(r.completionDate) = ?
                ORDER BY r.requestID
            ''', (date,))
            
            completed_requests = cursor.fetchall()
        
        # Формирование отчета
        report = f"""
        📊 ЕЖЕДНЕВНЫЙ ОТЧЕТ
        Дата: {date}
        
        СТАТИСТИКА:
        • Всего заявок: {stats[0] or 0}
        • Завершено: {stats[1] or 0}
        • Доход: {stats[2] or 0:.2f}₽
        • Уникальных клиентов: {stats[3] or 0}
        
        НОВЫЕ ЗАЯВКИ ({len(new_requests)}):
        """
        
        for req in new_requests:
            report += f"\n• #{req[0]} - {req[1]}: {req[2][:50]}..."
            if req[3]:
                report += f" (Клиент: {req[3]})"
            if req[4]:
                report += f" [Мастер: {req[4]}]"
        
        report += f"\n\nЗАВЕРШЕННЫЕ ЗАЯВКИ ({len(completed_requests)}):"
        
        for req in completed_requests:
            report += f"\n• #{req[0]} - {req[1]}: {req[2] or 0:.2f}₽"
            if req[3]:
                report += f" (Клиент: {req[3]})"
            if req[4]:
                report += f" [Мастер: {req[4]}]"
        
        return report
    
    @staticmethod
    def generate_master_report(db_connection, master_id, start_date, end_date):
        """Генерация отчета по мастеру"""
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Информация о мастере
            cursor.execute('SELECT fio, phone FROM users WHERE userID = ?', (master_id,))
            master_info = cursor.fetchone()
            
            # Статистика мастера
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                    AVG(CASE WHEN completionDate IS NOT NULL 
                        THEN julianday(completionDate) - julianday(startDate) 
                        ELSE NULL END) as avg_days,
                    SUM(actualCost) as revenue,
                    AVG(actualCost) as avg_revenue
                FROM requests 
                WHERE masterID = ? AND startDate BETWEEN ? AND ?
            ''', (master_id, start_date, end_date))
            
            stats = cursor.fetchone()
            
            # Заявки мастера
            cursor.execute('''
                SELECT requestID, startDate, homeTechType, requestStatus, actualCost
                FROM requests 
                WHERE masterID = ? AND startDate BETWEEN ? AND ?
                ORDER BY startDate DESC
            ''', (master_id, start_date, end_date))
            
            requests = cursor.fetchall()
        
        report = f"""
        👨‍🔧 ОТЧЕТ ПО МАСТЕРУ
        Период: {start_date} - {end_date}
        
        МАСТЕР:
        • ФИО: {master_info[0]}
        • Телефон: {master_info[1]}
        
        СТАТИСТИКА:
        • Всего заявок: {stats[0] or 0}
        • Завершено: {stats[1] or 0}
        • Среднее время ремонта: {stats[2] or 0:.1f} дней
        • Общий доход: {stats[3] or 0:.2f}₽
        • Средний чек: {stats[4] or 0:.2f}₽
        
        ЗАЯВКИ ({len(requests)}):
        """
        
        for req in requests:
            status_icon = {
                'Новая заявка': '🆕',
                'В процессе ремонта': '🔧',
                'Ожидание запчастей': '⏳',
                'Готова к выдаче': '✅'
            }.get(req[3], '❓')
            
            report += f"\n{status_icon} #{req[0]} - {req[1]} - {req[2]}"
            if req[4]:
                report += f" - {req[4]:.2f}₽"
        
        return report
    
    @staticmethod
    def generate_tech_type_report(db_connection, tech_type, start_date, end_date):
        """Генерация отчета по типу техники"""
        with db_connection.get_connection() as conn:
            cursor = conn.cursor()
            
            # Статистика по типу техники
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                    AVG(CASE WHEN completionDate IS NOT NULL 
                        THEN julianday(completionDate) - julianday(startDate) 
                        ELSE NULL END) as avg_days,
                    AVG(actualCost) as avg_cost,
                    SUM(actualCost) as total_cost,
                    MIN(actualCost) as min_cost,
                    MAX(actualCost) as max_cost
                FROM requests 
                WHERE homeTechType = ? AND startDate BETWEEN ? AND ?
            ''', (tech_type, start_date, end_date))
            
            stats = cursor.fetchone()
            
            # Распределение по моделям
            cursor.execute('''
                SELECT homeTechModel, COUNT(*) as count, AVG(actualCost) as avg_cost
                FROM requests 
                WHERE homeTechType = ? AND startDate BETWEEN ? AND ?
                GROUP BY homeTechModel
                ORDER BY count DESC
                LIMIT 10
            ''', (tech_type, start_date, end_date))
            
            models = cursor.fetchall()
            
            # Распределение по проблемам
            cursor.execute('''
                SELECT problemDescription, COUNT(*) as count
                FROM requests 
                WHERE homeTechType = ? AND startDate BETWEEN ? AND ?
                GROUP BY problemDescription
                ORDER BY count DESC
                LIMIT 10
            ''', (tech_type, start_date, end_date))
            
            problems = cursor.fetchall()
        
        report = f"""
        🏷️ ОТЧЕТ ПО ТИПУ ТЕХНИКИ
        Тип: {tech_type}
        Период: {start_date} - {end_date}
        
        ОБЩАЯ СТАТИСТИКА:
        • Всего заявок: {stats[0] or 0}
        • Завершено: {stats[1] or 0}
        • Среднее время ремонта: {stats[2] or 0:.1f} дней
        • Средняя стоимость: {stats[3] or 0:.2f}₽
        • Общая стоимость: {stats[4] or 0:.2f}₽
        • Минимальная стоимость: {stats[5] or 0:.2f}₽
        • Максимальная стоимость: {stats[6] or 0:.2f}₽
        
        ПОПУЛЯРНЫЕ МОДЕЛИ:
        """
        
        for model in models:
            report += f"\n• {model[0]}: {model[1]} заявок (ср. {model[2] or 0:.2f}₽)"
        
        report += f"\n\nЧАСТЫЕ ПРОБЛЕМЫ:"
        
        for problem in problems:
            report += f"\n• {problem[0][:50]}: {problem[1]} случаев"
        
        return report
    
    @staticmethod
    def generate_invoice(request_data, client_data, parts_data):
        """Генерация счета"""
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        invoice = f"""
        ╔══════════════════════════════════════════════════════════════╗
        ║                       СЧЕТ НА ОПЛАТУ                        ║
        ╠══════════════════════════════════════════════════════════════╣
        ║ Номер счета: {invoice_number:>44} ║
        ║ Дата: {datetime.now().strftime('%d.%m.%Y'):>52} ║
        ╠══════════════════════════════════════════════════════════════╣
        ║ ПОСТАВЩИК: Сервисный центр "IT-Соm"                         ║
        ║ ИНН: 1234567890                                             ║
        ║ Адрес: г. Москва, ул. Примерная, д. 1                       ║
        ╠══════════════════════════════════════════════════════════════╣
        ║ ПОКУПАТЕЛЬ: {client_data.get('fio', '')[:40]:<40} ║
        ║ Телефон: {client_data.get('phone', '')[:38]:<38} ║
        ╠══════════════════════════════════════════════════════════════╣
        ║ Заявка: #{request_data.get('requestID', '')}                ║
        ║ Техника: {request_data.get('homeTechType', '')} - {request_data.get('homeTechModel', '')[:25]:<25} ║
        ╠══════════════════════════════════════════════════════════════╣
        ║ №  Наименование                    Кол-во   Цена      Сумма  ║
        ╠══════════════════════════════════════════════════════════════╣
        """
        
        total = 0
        row_num = 1
        
        # Запчасти
        for part in parts_data:
            name = part.get('partName', '')[:25]
            quantity = part.get('quantity', 1)
            price = part.get('price', 0)
            sum_price = quantity * price
            total += sum_price
            
            invoice += f"║ {row_num:2} {name:<25} {quantity:>7} {price:>8.2f}₽ {sum_price:>9.2f}₽ ║\n"
            row_num += 1
        
        # Работа мастера
        labor_cost = request_data.get('actualCost', 0) - total
        if labor_cost > 0:
            invoice += f"║ {row_num:2} Работа мастера{' ':>17} 1 {labor_cost:>8.2f}₽ {labor_cost:>9.2f}₽ ║\n"
            total += labor_cost
        
        invoice += f"""╠══════════════════════════════════════════════════════════════╣
        ║ ИТОГО: {' ':>43} {total:>9.2f}₽ ║
        ╚══════════════════════════════════════════════════════════════╝
        
        Всего наименований: {row_num-1}, на сумму: {total:.2f}₽
        
        Подпись поставщика: _________________    М.П.
        
        Счет действителен в течение 5 банковских дней.
        """
        
        return invoice, invoice_number

class CodeGenerator:
    """Генератор кодов"""
    
    @staticmethod
    def generate_request_number() -> str:
        """Генерация номера заявки"""
        timestamp = datetime.now().strftime('%y%m%d')
        random_part = random.randint(1000, 9999)
        return f"REQ-{timestamp}-{random_part}"
    
    @staticmethod
    def generate_vendor_code(prefix: str = "PART") -> str:
        """Генерация артикула"""
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{prefix}-{random_part}"
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Генерация пароля"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def generate_activation_code() -> str:
        """Генерация кода активации"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))