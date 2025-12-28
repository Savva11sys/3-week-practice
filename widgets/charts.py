import tkinter as tk
from tkinter import ttk
from styles import StyleManager
import math

class PieChart(tk.Canvas):
    """Круговая диаграмма"""
    def __init__(self, parent, width=300, height=300, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=StyleManager.COLORS['white'],
                        highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.data = {}
        self.colors = []
        
        # Цвета по умолчанию
        self.default_colors = [
            StyleManager.COLORS['secondary'],
            StyleManager.COLORS['success'],
            StyleManager.COLORS['warning'],
            StyleManager.COLORS['danger'],
            StyleManager.COLORS['info'],
            StyleManager.COLORS['primary'],
            StyleManager.COLORS['gray']
        ]
    
    def set_data(self, data, colors=None):
        """Установить данные для диаграммы"""
        self.data = data
        self.colors = colors or self.default_colors
        self._draw()
    
    def _draw(self):
        self.delete("all")
        
        if not self.data:
            # Отображаем сообщение об отсутствии данных
            self.create_text(self.width//2, self.height//2,
                           text="Нет данных",
                           fill=StyleManager.COLORS['gray'],
                           font=StyleManager.FONTS['body'])
            return
        
        total = sum(self.data.values())
        if total == 0:
            return
        
        center_x = self.width // 2
        center_y = self.height // 2
        radius = min(center_x, center_y) - 40
        
        start_angle = 90  # Начинаем сверху
        
        # Рисуем сегменты
        segments = []
        for i, (label, value) in enumerate(self.data.items()):
            angle = 360 * (value / total)
            
            # Цвет сегмента
            color = self.colors[i % len(self.colors)]
            
            # Координаты дуги
            x1 = center_x - radius
            y1 = center_y - radius
            x2 = center_x + radius
            y2 = center_y + radius
            
            # Рисуем сегмент
            segment = self.create_arc(x1, y1, x2, y2,
                                    start=start_angle, extent=angle,
                                    fill=color, outline=StyleManager.COLORS['white'],
                                    width=2)
            segments.append((segment, label, value, color, start_angle, angle))
            
            start_angle += angle
        
        # Легенда
        legend_x = self.width - 150
        legend_y = 30
        
        for i, (segment, label, value, color, start_angle, angle) in enumerate(segments):
            # Квадратик цвета
            self.create_rectangle(legend_x, legend_y + i*25,
                                legend_x + 15, legend_y + i*25 + 15,
                                fill=color, outline=StyleManager.COLORS['gray_dark'])
            
            # Процент
            percentage = (value / total) * 100
            
            # Текст
            text = f"{label}: {value} ({percentage:.1f}%)"
            self.create_text(legend_x + 25, legend_y + i*25 + 7,
                           text=text,
                           anchor=tk.W,
                           fill=StyleManager.COLORS['dark'],
                           font=StyleManager.FONTS['small'])
        
        # Центральный текст (общее количество)
        self.create_text(center_x, center_y,
                       text=str(total),
                       fill=StyleManager.COLORS['dark'],
                       font=('Segoe UI', 16, 'bold'))
        
        self.create_text(center_x, center_y + 20,
                       text="Всего",
                       fill=StyleManager.COLORS['gray_dark'],
                       font=StyleManager.FONTS['small'])

class BarChart(tk.Canvas):
    """Столбчатая диаграмма"""
    def __init__(self, parent, width=400, height=300, title="", **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=StyleManager.COLORS['white'],
                        highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.title = title
        self.data = {}
        self.colors = []
        
        # Цвета по умолчанию
        self.default_colors = [
            StyleManager.COLORS['secondary'],
            StyleManager.COLORS['success'],
            StyleManager.COLORS['warning'],
            StyleManager.COLORS['danger'],
            StyleManager.COLORS['info']
        ]
    
    def set_data(self, data, colors=None):
        """Установить данные для диаграммы"""
        self.data = data
        self.colors = colors or self.default_colors
        self._draw()
    
    def _draw(self):
        self.delete("all")
        
        if not self.data:
            # Отображаем сообщение об отсутствии данных
            self.create_text(self.width//2, self.height//2,
                           text="Нет данных",
                           fill=StyleManager.COLORS['gray'],
                           font=StyleManager.FONTS['body'])
            return
        
        # Заголовок
        if self.title:
            self.create_text(self.width//2, 20,
                           text=self.title,
                           fill=StyleManager.COLORS['dark'],
                           font=StyleManager.FONTS['heading'])
        
        padding = 60
        chart_width = self.width - padding * 2
        chart_height = self.height - padding * 2
        
        max_value = max(self.data.values()) if self.data else 1
        bar_width = chart_width / (len(self.data) * 1.5)
        
        x = padding + bar_width / 4
        color_index = 0
        
        # Оси
        self.create_line(padding, self.height - padding,
                        self.width - padding, self.height - padding,
                        fill=StyleManager.COLORS['gray_dark'], width=2)
        
        self.create_line(padding, padding,
                        padding, self.height - padding,
                        fill=StyleManager.COLORS['gray_dark'], width=2)
        
        # Сетка
        grid_lines = 5
        for i in range(grid_lines + 1):
            y = padding + (chart_height * i / grid_lines)
            value = max_value * (1 - i / grid_lines)
            
            # Горизонтальная линия сетки
            self.create_line(padding, y, self.width - padding, y,
                           fill=StyleManager.COLORS['light_dark'], 
                           dash=(2, 2))
            
            # Подпись значения
            self.create_text(padding - 10, y,
                           text=f"{value:.0f}",
                           anchor=tk.E,
                           fill=StyleManager.COLORS['gray_dark'],
                           font=StyleManager.FONTS['small'])
        
        for label, value in self.data.items():
            bar_height = (value / max_value) * chart_height
            
            # Рисуем столбец
            x1 = x
            y1 = self.height - padding - bar_height
            x2 = x + bar_width
            y2 = self.height - padding
            
            color = self.colors[color_index % len(self.colors)]
            
            # Основной прямоугольник
            self.create_rectangle(x1, y1, x2, y2,
                                fill=color,
                                outline=StyleManager.COLORS['gray_dark'])
            
            # Верхняя грань (для 3D эффекта)
            self.create_polygon(x1, y1, x2, y1, 
                              x2+2, y1-2, x1+2, y1-2,
                              fill=StyleManager.lighten_color(color, 0.3),
                              outline='')
            
            # Правая грань (для 3D эффекта)
            self.create_polygon(x2, y1, x2, y2,
                              x2+2, y2-2, x2+2, y1-2,
                              fill=StyleManager.darken_color(color, 0.3),
                              outline='')
            
            # Подпись значения
            self.create_text(x + bar_width/2, y1 - 10,
                           text=str(value),
                           fill=StyleManager.COLORS['dark'],
                           font=StyleManager.FONTS['small_bold'])
            
            # Подпись категории
            label_y = self.height - padding + 20
            label_text = label if len(label) <= 15 else label[:12] + "..."
            
            self.create_text(x + bar_width/2, label_y,
                           text=label_text,
                           fill=StyleManager.COLORS['dark'],
                           font=StyleManager.FONTS['small'])
            
            x += bar_width * 1.5
            color_index += 1
        
        # Подпись оси Y
        self.create_text(padding//2, padding//2,
                       text="Количество",
                       angle=90,
                       fill=StyleManager.COLORS['dark'],
                       font=StyleManager.FONTS['small'])

class LineChart(tk.Canvas):
    """Линейный график"""
    def __init__(self, parent, width=400, height=300, title="", **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=StyleManager.COLORS['white'],
                        highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.title = title
        self.data = []  # Список кортежей (x, y)
        self.color = StyleManager.COLORS['secondary']
    
    def set_data(self, data, color=None):
        """Установить данные для графика"""
        self.data = data
        if color:
            self.color = color
        self._draw()
    
    def _draw(self):
        self.delete("all")
        
        if len(self.data) < 2:
            # Отображаем сообщение об отсутствии данных
            self.create_text(self.width//2, self.height//2,
                           text="Недостаточно данных",
                           fill=StyleManager.COLORS['gray'],
                           font=StyleManager.FONTS['body'])
            return
        
        # Заголовок
        if self.title:
            self.create_text(self.width//2, 20,
                           text=self.title,
                           fill=StyleManager.COLORS['dark'],
                           font=StyleManager.FONTS['heading'])
        
        padding = 60
        chart_width = self.width - padding * 2
        chart_height = self.height - padding * 2
        
        # Находим мин/макс значения
        x_values = [point[0] for point in self.data]
        y_values = [point[1] for point in self.data]
        
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)
        
        # Масштабируем данные
        scaled_points = []
        for x, y in self.data:
            scaled_x = padding + ((x - min_x) / (max_x - min_x)) * chart_width if max_x != min_x else padding
            scaled_y = self.height - padding - ((y - min_y) / (max_y - min_y)) * chart_height if max_y != min_y else self.height - padding
            scaled_points.append((scaled_x, scaled_y))
        
        # Оси
        self.create_line(padding, self.height - padding,
                        self.width - padding, self.height - padding,
                        fill=StyleManager.COLORS['gray_dark'], width=2)
        
        self.create_line(padding, padding,
                        padding, self.height - padding,
                        fill=StyleManager.COLORS['gray_dark'], width=2)
        
        # Рисуем линию
        for i in range(1, len(scaled_points)):
            x1, y1 = scaled_points[i-1]
            x2, y2 = scaled_points[i]
            
            # Линия
            self.create_line(x1, y1, x2, y2,
                           fill=self.color, width=3, smooth=True)
            
            # Точки
            self.create_oval(x1-4, y1-4, x1+4, y1+4,
                           fill=self.color,
                           outline=StyleManager.COLORS['white'],
                           width=2)
        
        # Последняя точка
        if scaled_points:
            x_last, y_last = scaled_points[-1]
            self.create_oval(x_last-4, y_last-4, x_last+4, y_last+4,
                           fill=self.color,
                           outline=StyleManager.COLORS['white'],
                           width=2)
        
        # Подписи осей
        self.create_text(padding//2, padding//2,
                       text="Значение",
                       angle=90,
                       fill=StyleManager.COLORS['dark'],
                       font=StyleManager.FONTS['small'])
        
        # Подписи точек
        for i, ((x, y), (scaled_x, scaled_y)) in enumerate(zip(self.data, scaled_points)):
            if i % max(1, len(self.data)//5) == 0:  # Показываем примерно 5 подписей
                self.create_text(scaled_x, self.height - padding + 15,
                               text=str(x),
                               fill=StyleManager.COLORS['dark'],
                               font=StyleManager.FONTS['small'])
                
                self.create_text(padding - 15, scaled_y,
                               text=str(y),
                               anchor=tk.E,
                               fill=StyleManager.COLORS['dark'],
                               font=StyleManager.FONTS['small'])

class GaugeChart(tk.Canvas):
    """Спидометр/датчик"""
    def __init__(self, parent, width=200, height=200, 
                 min_value=0, max_value=100, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=StyleManager.COLORS['white'],
                        highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value
        self.title = ""
        self.unit = ""
    
    def set_value(self, value, title="", unit=""):
        """Установить значение датчика"""
        self.value = max(self.min_value, min(self.max_value, value))
        self.title = title
        self.unit = unit
        self._draw()
    
    def _draw(self):
        self.delete("all")
        
        center_x = self.width // 2
        center_y = self.height - 30
        radius = min(center_x, center_y) - 20
        
        # Фон датчика
        start_angle = 180
        end_angle = 0
        extent = end_angle - start_angle
        
        # Цветовые зоны
        zones = [
            (0.0, 0.3, StyleManager.COLORS['success']),   # 0-30% - зеленый
            (0.3, 0.7, StyleManager.COLORS['warning']),   # 30-70% - оранжевый
            (0.7, 1.0, StyleManager.COLORS['danger'])     # 70-100% - красный
        ]
        
        # Рисуем цветовые зоны
        for zone_start, zone_end, color in zones:
            zone_extent = extent * (zone_end - zone_start)
            zone_start_angle = start_angle + extent * zone_start
            
            self.create_arc(center_x - radius, center_y - radius,
                          center_x + radius, center_y + radius,
                          start=zone_start_angle, extent=zone_extent,
                          style=tk.ARC,
                          outline=color,
                          width=15)
        
        # Текущее значение
        percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
        needle_angle = start_angle + extent * percentage
        
        # Рисуем стрелку
        needle_length = radius * 0.8
        needle_x = center_x + needle_length * math.cos(math.radians(needle_angle))
        needle_y = center_y - needle_length * math.sin(math.radians(needle_angle))
        
        self.create_line(center_x, center_y, needle_x, needle_y,
                        fill=StyleManager.COLORS['dark'],
                        width=3)
        
        # Центральная точка
        self.create_oval(center_x-8, center_y-8, center_x+8, center_y+8,
                        fill=StyleManager.COLORS['dark'],
                        outline='')
        
        # Отображение значения
        value_text = f"{self.value:.1f}{self.unit}"
        self.create_text(center_x, center_y - radius//2,
                       text=value_text,
                       fill=StyleManager.COLORS['dark'],
                       font=('Segoe UI', 16, 'bold'))
        
        # Заголовок
        if self.title:
            self.create_text(center_x, 20,
                           text=self.title,
                           fill=StyleManager.COLORS['dark'],
                           font=StyleManager.FONTS['body_bold'])
        
        # Минимальное и максимальное значения
        self.create_text(center_x - radius, center_y + 10,
                       text=str(self.min_value),
                       fill=StyleManager.COLORS['gray_dark'],
                       font=StyleManager.FONTS['small'])
        
        self.create_text(center_x + radius, center_y + 10,
                       text=str(self.max_value),
                       fill=StyleManager.COLORS['gray_dark'],
                       font=StyleManager.FONTS['small'])