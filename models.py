from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserType(Enum):
    """Типы пользователей"""
    MANAGER = "Менеджер"
    MASTER = "Мастер"
    OPERATOR = "Оператор"
    CLIENT = "Заказчик"
    QUALITY_MANAGER = "Менеджер качества"

class RequestStatus(Enum):
    """Статусы заявок"""
    NEW = "Новая заявка"
    IN_PROGRESS = "В процессе ремонта"
    WAITING_PARTS = "Ожидание запчастей"
    READY = "Готова к выдаче"

class Priority(Enum):
    """Приоритеты заявок"""
    LOW = 5
    MEDIUM_LOW = 4
    MEDIUM = 3
    MEDIUM_HIGH = 2
    HIGH = 1

@dataclass
class User:
    """Модель пользователя"""
    userID: int
    fio: str
    phone: str
    login: str
    password: str
    type: str
    created_at: Optional[str] = None
    is_active: bool = True
    
    def get_type_display(self) -> str:
        """Получить отображаемое название типа"""
        return self.type
    
    def is_manager(self) -> bool:
        """Является ли менеджером"""
        return self.type == UserType.MANAGER.value
    
    def is_master(self) -> bool:
        """Является ли мастером"""
        return self.type == UserType.MASTER.value
    
    def is_operator(self) -> bool:
        """Является ли оператором"""
        return self.type == UserType.OPERATOR.value
    
    def is_client(self) -> bool:
        """Является ли клиентом"""
        return self.type == UserType.CLIENT.value
    
    def is_quality_manager(self) -> bool:
        """Является ли менеджером качества"""
        return self.type == UserType.QUALITY_MANAGER.value
    
    def has_permission(self, permission: str) -> bool:
        """Проверка разрешений"""
        permissions = {
            'create_request': [UserType.MANAGER.value, UserType.OPERATOR.value],
            'edit_request': [UserType.MANAGER.value, UserType.OPERATOR.value, UserType.MASTER.value],
            'delete_request': [UserType.MANAGER.value],
            'assign_master': [UserType.MANAGER.value, UserType.OPERATOR.value],
            'view_statistics': [UserType.MANAGER.value, UserType.OPERATOR.value, UserType.QUALITY_MANAGER.value],
            'quality_control': [UserType.QUALITY_MANAGER.value]
        }
        
        return self.type in permissions.get(permission, [])

@dataclass
class Request:
    """Модель заявки"""
    requestID: int
    startDate: str
    homeTechType: str
    homeTechModel: str
    problemDescription: str
    requestStatus: str
    completionDate: Optional[str]
    repairParts: Optional[str]
    masterID: Optional[int]
    clientID: int
    qualityManagerID: Optional[int] = None
    extendedDeadline: Optional[str] = None
    estimatedCost: float = 0.0
    actualCost: float = 0.0
    priority: int = 3
    notes: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Дополнительные поля (заполняются при выборке)
    client_name: Optional[str] = None
    master_name: Optional[str] = None
    quality_manager_name: Optional[str] = None
    
    def get_status_color(self) -> str:
        """Получить цвет для статуса"""
        colors = {
            RequestStatus.NEW.value: "#3498db",  # Синий
            RequestStatus.IN_PROGRESS.value: "#f39c12",  # Оранжевый
            RequestStatus.WAITING_PARTS.value: "#e74c3c",  # Красный
            RequestStatus.READY.value: "#2ecc71"  # Зеленый
        }
        return colors.get(self.requestStatus, "#95a5a6")  # Серый по умолчанию
    
    def get_priority_color(self) -> str:
        """Получить цвет для приоритета"""
        colors = {
            Priority.HIGH.value: "#e74c3c",  # Красный
            Priority.MEDIUM_HIGH.value: "#e67e22",  # Оранжевый
            Priority.MEDIUM.value: "#f1c40f",  # Желтый
            Priority.MEDIUM_LOW.value: "#3498db",  # Синий
            Priority.LOW.value: "#2ecc71"  # Зеленый
        }
        return colors.get(self.priority, "#95a5a6")
    
    def get_priority_text(self) -> str:
        """Получить текст приоритета"""
        texts = {
            Priority.HIGH.value: "Высокий",
            Priority.MEDIUM_HIGH.value: "Выше среднего",
            Priority.MEDIUM.value: "Средний",
            Priority.MEDIUM_LOW.value: "Ниже среднего",
            Priority.LOW.value: "Низкий"
        }
        return texts.get(self.priority, "Не указан")
    
    def calculate_repair_days(self) -> Optional[int]:
        """Рассчитать количество дней ремонта"""
        if not self.startDate:
            return None
        
        start = datetime.strptime(self.startDate, "%Y-%m-%d")
        
        if self.completionDate:
            end = datetime.strptime(self.completionDate, "%Y-%m-%d")
            return (end - start).days
        else:
            end = datetime.now()
            return (end - start).days
    
    def is_overdue(self, threshold_days=7) -> bool:
        """Проверить, просрочена ли заявка"""
        days = self.calculate_repair_days()
        return days is not None and days > threshold_days and self.requestStatus != RequestStatus.READY.value
    
    def is_completed(self) -> bool:
        """Проверить, завершена ли заявка"""
        return self.requestStatus == RequestStatus.READY.value
    
    def can_be_completed(self) -> bool:
        """Можно ли завершить заявку"""
        return self.requestStatus in [RequestStatus.NEW.value, RequestStatus.IN_PROGRESS.value, RequestStatus.WAITING_PARTS.value]
    
    def get_progress_percentage(self) -> int:
        """Получить процент выполнения"""
        status_progress = {
            RequestStatus.NEW.value: 25,
            RequestStatus.WAITING_PARTS.value: 50,
            RequestStatus.IN_PROGRESS.value: 75,
            RequestStatus.READY.value: 100
        }
        return status_progress.get(self.requestStatus, 0)

@dataclass
class Comment:
    """Модель комментария"""
    commentID: int
    message: str
    masterID: int
    requestID: int
    timestamp: Optional[str] = None
    is_private: bool = False
    
    # Дополнительные поля
    master_name: Optional[str] = None
    
    def format_timestamp(self) -> str:
        """Форматирование времени"""
        if not self.timestamp:
            return ""
        
        try:
            dt = datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d.%m.%Y %H:%M")
        except:
            return self.timestamp

@dataclass
class Part:
    """Модель запчасти"""
    partID: int
    partName: str
    vendorCode: str
    price: float
    quantity: int
    min_quantity: int = 5
    supplier: Optional[str] = None
    last_ordered: Optional[str] = None
    
    def is_low_stock(self) -> bool:
        """Проверить, низкий ли запас"""
        return self.quantity <= self.min_quantity
    
    def get_stock_status_color(self) -> str:
        """Получить цвет статуса запаса"""
        if self.quantity == 0:
            return "#e74c3c"  # Красный
        elif self.is_low_stock():
            return "#f39c12"  # Оранжевый
        else:
            return "#2ecc71"  # Зеленый

@dataclass
class Notification:
    """Модель уведомления"""
    notificationID: int
    userID: int
    message: str
    type: str
    is_read: bool = False
    created_at: Optional[str] = None
    
    def get_type_color(self) -> str:
        """Получить цвет типа уведомления"""
        colors = {
            'info': '#3498db',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'success': '#2ecc71'
        }
        return colors.get(self.type, '#95a5a6')
    
    def format_time_ago(self) -> str:
        """Форматировать время "сколько времени назад" """
        if not self.created_at:
            return ""
        
        try:
            created = datetime.strptime(self.created_at, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            diff = now - created
            
            if diff.days > 0:
                return f"{diff.days} дн. назад"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} ч. назад"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} мин. назад"
            else:
                return "Только что"
        except:
            return self.created_at

@dataclass
class Statistics:
    """Модель статистики"""
    total_requests: int = 0
    active_requests: int = 0
    completed_requests: int = 0
    avg_repair_days: float = 0.0
    total_revenue: float = 0.0
    unique_clients: int = 0
    by_status: dict = None
    by_tech_type: list = None
    by_master: list = None
    by_month: list = None
    
    def __post_init__(self):
        if self.by_status is None:
            self.by_status = {}
        if self.by_tech_type is None:
            self.by_tech_type = []
        if self.by_master is None:
            self.by_master = []
        if self.by_month is None:
            self.by_month = []
    
    def get_completion_rate(self) -> float:
        """Получить процент завершения"""
        if self.total_requests == 0:
            return 0.0
        return (self.completed_requests / self.total_requests) * 100
    
    def get_average_revenue_per_request(self) -> float:
        """Получить средний доход на заявку"""
        if self.completed_requests == 0:
            return 0.0
        return self.total_revenue / self.completed_requests