import tkinter as tk
from tkinter import ttk
from styles import StyleManager, create_rounded_rectangle, create_shadow, add_hover_effect
from PIL import Image, ImageTk
import os

class Card(ttk.Frame):
    """Виджет карточки"""
    def __init__(self, parent, title="", padding=10, rounded=False, shadow=False, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        self.title = title
        self.padding = padding
        self.rounded = rounded
        self.shadow = shadow
        
        if title:
            self.title_label = ttk.Label(self, text=title, 
                                       style='Heading.TLabel')
            self.title_label.pack(side=tk.TOP, fill=tk.X, 
                                padx=padding, pady=(padding, padding//2))
        
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, 
                              padx=padding, pady=padding//2)
    
    def add_widget(self, widget, **pack_options):
        """Добавить виджет в карточку"""
        default_options = {'fill': tk.X, 'padx': 5, 'pady': 2}
        default_options.update(pack_options)
        widget.pack(**default_options)

class MetricCard(Card):
    """Карточка с метрикой"""
    def __init__(self, parent, title, value, unit="", icon=None, 
                 trend=None, color=None, **kwargs):
        super().__init__(parent, title, **kwargs)
        
        self.value_var = tk.StringVar(value=str(value))
        self.unit_var = tk.StringVar(value=unit)
        self.trend_var = tk.StringVar(value=trend or "")
        
        # Основное значение
        value_frame = ttk.Frame(self.content_frame)
        value_frame.pack(fill=tk.X, expand=True)
        
        self.value_label = ttk.Label(value_frame,
                                    textvariable=self.value_var,
                                    font=('Segoe UI', 28, 'bold'),
                                    foreground=color or StyleManager.COLORS['secondary'])
        self.value_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Единица измерения
        if unit:
            unit_frame = ttk.Frame(value_frame)
            unit_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            ttk.Label(unit_frame,
                     textvariable=self.unit_var,
                     font=StyleManager.FONTS['body'],
                     foreground=StyleManager.COLORS['gray_dark']).pack(anchor=tk.NW)
        
        # Тренд (если есть)
        if trend:
            trend_color = StyleManager.COLORS['success'] if trend.startswith('+') else StyleManager.COLORS['danger']
            ttk.Label(value_frame, textvariable=self.trend_var,
                     font=StyleManager.FONTS['small_bold'],
                     foreground=trend_color).pack(side=tk.RIGHT, padx=5)
        
        # Иконка (если есть)
        if icon:
            icon_label = ttk.Label(self.content_frame, text=icon,
                                  font=('Segoe UI Symbol', 24),
                                  foreground=color or StyleManager.COLORS['secondary'])
            icon_label.pack(side=tk.RIGHT, padx=5)
    
    def update_value(self, value, unit=None, trend=None):
        """Обновить значение метрики"""
        self.value_var.set(str(value))
        if unit:
            self.unit_var.set(unit)
        if trend:
            self.trend_var.set(trend)

class ProgressBar(tk.Canvas):
    """Кастомный прогресс-бар"""
    def __init__(self, parent, width=200, height=20, value=0, 
                 show_percentage=True, rounded=True, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=StyleManager.COLORS['light'], 
                        highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.value = value
        self.show_percentage = show_percentage
        self.rounded = rounded
        
        # Создание элементов
        self._create_elements()
        self.set_value(value)
    
    def _create_elements(self):
        """Создание элементов прогресс-бара"""
        # Фон
        if self.rounded:
            self.bg_rect = create_rounded_rectangle(self, 0, 0, 
                                                   self.width, self.height,
                                                   radius=self.height//2,
                                                   fill=StyleManager.COLORS['light_dark'],
                                                   outline='')
        else:
            self.bg_rect = self.create_rectangle(0, 0, self.width, self.height,
                                                fill=StyleManager.COLORS['light_dark'],
                                                outline='')
        
        # Прогресс
        if self.rounded:
            self.progress_rect = create_rounded_rectangle(self, 0, 0, 0, self.height,
                                                         radius=self.height//2,
                                                         fill=StyleManager.COLORS['secondary'],
                                                         outline='')
        else:
            self.progress_rect = self.create_rectangle(0, 0, 0, self.height,
                                                      fill=StyleManager.COLORS['secondary'],
                                                      outline='')
        
        # Текст процентов
        if self.show_percentage:
            self.text = self.create_text(self.width//2, self.height//2,
                                       text="0%",
                                       fill=StyleManager.COLORS['dark'],
                                       font=StyleManager.FONTS['small_bold'])
    
    def set_value(self, value):
        """Установить значение (0-100)"""
        self.value = max(0, min(100, value))
        progress_width = (self.width * self.value) // 100
        
        if self.rounded:
            self.coords(self.progress_rect, 0, 0, progress_width, self.height)
        else:
            self.coords(self.progress_rect, 0, 0, progress_width, self.height)
        
        if self.show_percentage:
            self.itemconfig(self.text, text=f"{self.value}%")
        
        # Изменение цвета в зависимости от значения
        if self.value < 30:
            color = StyleManager.COLORS['danger']
        elif self.value < 70:
            color = StyleManager.COLORS['warning']
        else:
            color = StyleManager.COLORS['success']
        
        self.itemconfig(self.progress_rect, fill=color)
    
    def get_value(self):
        """Получить текущее значение"""
        return self.value

class SearchBox(ttk.Frame):
    """Поле поиска с иконкой"""
    def __init__(self, parent, placeholder="Поиск...", 
                 on_search=None, width=30, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.on_search_callback = on_search
        self.search_var = tk.StringVar()
        
        # Стиль для поля поиска
        self.configure(style='Card.TFrame')
        
        # Иконка поиска
        self.search_icon = ttk.Label(self, text="🔍", 
                                    font=('Segoe UI', 14),
                                    foreground=StyleManager.COLORS['gray_dark'])
        self.search_icon.pack(side=tk.LEFT, padx=(10, 5))
        
        # Поле ввода
        self.entry = ttk.Entry(self, textvariable=self.search_var,
                              style='Modern.TEntry', width=width)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, 
                       padx=5, pady=8)
        
        # Кнопка очистки
        self.clear_btn = ttk.Button(self, text="×", 
                                   style='Flat.TButton',
                                   command=self.clear_search,
                                   width=2)
        self.clear_btn.pack(side=tk.RIGHT, padx=(0, 10))
        self.clear_btn.pack_forget()  # Скрываем по умолчанию
        
        # Установка placeholder
        self.entry.insert(0, placeholder)
        self.entry.configure(foreground=StyleManager.COLORS['gray'])
        
        # Бинды
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.search_var.trace('w', self._on_text_change)
        
        # Эффект наведения
        add_hover_effect(self, StyleManager.COLORS['white'], 
                        StyleManager.COLORS['light'])
    
    def _on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(foreground=StyleManager.COLORS['dark'])
    
    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(foreground=StyleManager.COLORS['gray'])
    
    def _on_key_release(self, event):
        if self.on_search_callback:
            self.on_search_callback(self.get())
    
    def _on_text_change(self, *args):
        text = self.search_var.get()
        if text and text != self.placeholder:
            self.clear_btn.pack(side=tk.RIGHT, padx=(0, 10))
        else:
            self.clear_btn.pack_forget()
    
    def get(self):
        """Получить текст поиска"""
        text = self.search_var.get()
        return text if text != self.placeholder else ""
    
    def clear_search(self):
        """Очистить поле поиска"""
        self.search_var.set("")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.configure(foreground=StyleManager.COLORS['gray'])
        self.clear_btn.pack_forget()
        
        if self.on_search_callback:
            self.on_search_callback("")
    
    def set_callback(self, callback):
        """Установить callback для поиска"""
        self.on_search_callback = callback
    
    def focus_search(self):
        """Установить фокус на поле поиска"""
        self.entry.focus()
        self._on_focus_in(None)

class StatusBadge(tk.Frame):
    """Бейдж статуса"""
    def __init__(self, parent, status, size='medium', **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status = status
        self.size = size
        
        # Определяем цвета и текст
        self.colors = self._get_status_colors()
        color = self.colors.get(status, StyleManager.COLORS['gray'])
        
        # Определяем размеры
        sizes = {
            'small': {'font': StyleManager.FONTS['small'], 'padding': (3, 6)},
            'medium': {'font': StyleManager.FONTS['body'], 'padding': (6, 10)},
            'large': {'font': StyleManager.FONTS['subheading'], 'padding': (8, 12)}
        }
        size_config = sizes.get(size, sizes['medium'])
        
        # Создаем метку
        self.label = tk.Label(self, text=status,
                             bg=color,
                             fg=StyleManager.COLORS['white'],
                             font=size_config['font'],
                             padx=size_config['padding'][0],
                             pady=size_config['padding'][1],
                             borderwidth=0,
                             relief='flat')
        self.label.pack()
        
        # Делаем фон прозрачным
        self.configure(bg=parent.cget('bg'))
    
    def _get_status_colors(self):
        """Получить цвета для статусов"""
        return {
            'Новая заявка': StyleManager.COLORS['status_new'],
            'В процессе ремонта': StyleManager.COLORS['status_in_progress'],
            'Ожидание запчастей': StyleManager.COLORS['status_waiting'],
            'Готова к выдаче': StyleManager.COLORS['status_ready']
        }
    
    def update_status(self, new_status):
        """Обновить статус"""
        self.status = new_status
        color = self.colors.get(new_status, StyleManager.COLORS['gray'])
        self.label.configure(text=new_status, bg=color)

class PriorityBadge(StatusBadge):
    """Бейдж приоритета"""
    def __init__(self, parent, priority, size='medium', **kwargs):
        # Преобразуем числовой приоритет в текст
        priority_texts = {
            1: 'Высокий',
            2: 'Выше среднего',
            3: 'Средний',
            4: 'Ниже среднего',
            5: 'Низкий'
        }
        
        status = priority_texts.get(priority, 'Не указан')
        super().__init__(parent, status, size, **kwargs)
        
        # Обновляем цвета для приоритетов
        self.colors = {
            'Высокий': StyleManager.COLORS['priority_high'],
            'Выше среднего': StyleManager.COLORS['priority_medium_high'],
            'Средний': StyleManager.COLORS['priority_medium'],
            'Ниже среднего': StyleManager.COLORS['priority_medium_low'],
            'Низкий': StyleManager.COLORS['priority_low'],
            'Не указан': StyleManager.COLORS['gray']
        }
        
        color = self.colors.get(status, StyleManager.COLORS['gray'])
        self.label.configure(bg=color)

class NotificationBadge(tk.Label):
    """Бейдж уведомлений"""
    def __init__(self, parent, count=0, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.count = count
        self.configure(
            text=str(count) if count > 0 else "",
            bg=StyleManager.COLORS['danger'],
            fg=StyleManager.COLORS['white'],
            font=StyleManager.FONTS['small_bold'],
            padx=6,
            pady=2,
            borderwidth=0,
            relief='flat'
        )
    
    def update_count(self, count):
        """Обновить количество уведомлений"""
        self.count = count
        if count > 0:
            self.configure(text=str(count))
            self.pack()
        else:
            self.configure(text="")
            self.pack_forget()
    
    def increment(self, amount=1):
        """Увеличить счетчик"""
        self.update_count(self.count + amount)
    
    def decrement(self, amount=1):
        """Уменьшить счетчик"""
        self.update_count(max(0, self.count - amount))

class LoadingSpinner(tk.Canvas):
    """Спиннер загрузки"""
    def __init__(self, parent, size=40, thickness=4, color=None, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        bg=StyleManager.COLORS['light'],
                        highlightthickness=0, **kwargs)
        
        self.size = size
        self.thickness = thickness
        self.color = color or StyleManager.COLORS['secondary']
        self.angle = 0
        self.is_spinning = False
        
        # Создаем арку
        self.arc = self.create_arc(
            thickness, thickness, 
            size-thickness, size-thickness,
            start=0, extent=0,
            outline=self.color,
            width=thickness,
            style=tk.ARC
        )
    
    def start(self):
        """Запустить спиннер"""
        self.is_spinning = True
        self._animate()
    
    def stop(self):
        """Остановить спиннер"""
        self.is_spinning = False
    
    def _animate(self):
        """Анимация спиннера"""
        if not self.is_spinning:
            return
        
        self.angle = (self.angle + 10) % 360
        self.coords(self.arc, 
                   self.thickness, self.thickness,
                   self.size-self.thickness, self.size-self.thickness)
        self.itemconfig(self.arc, start=self.angle, extent=70)
        
        self.after(50, self._animate)

class Avatar(tk.Canvas):
    """Аватар пользователя"""
    def __init__(self, parent, text="", size=40, color=None, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, **kwargs)
        
        self.size = size
        self.text = text[:2].upper()
        self.color = color or StyleManager.COLORS['secondary']
        
        # Создаем круг
        self.create_oval(2, 2, size-2, size-2,
                        fill=self.color,
                        outline=StyleManager.COLORS['light_dark'],
                        width=1)
        
        # Текст
        self.create_text(size//2, size//2,
                        text=self.text,
                        fill=StyleManager.COLORS['white'],
                        font=('Segoe UI', size//3, 'bold'))
    
    def update_text(self, new_text):
        """Обновить текст аватара"""
        self.text = new_text[:2].upper()
        self.delete("all")
        
        # Создаем круг
        self.create_oval(2, 2, self.size-2, self.size-2,
                        fill=self.color,
                        outline=StyleManager.COLORS['light_dark'],
                        width=1)
        
        # Текст
        self.create_text(self.size//2, self.size//2,
                        text=self.text,
                        fill=StyleManager.COLORS['white'],
                        font=('Segoe UI', self.size//3, 'bold'))