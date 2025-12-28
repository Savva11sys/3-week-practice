import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class StyleManager:
    """Менеджер стилей для приложения"""
    
    # Современная цветовая палитра
    COLORS = {
        'primary': '#2c3e50',      # Темно-синий
        'primary_light': '#34495e',
        'secondary': '#3498db',    # Синий
        'secondary_light': '#5dade2',
        'success': '#2ecc71',      # Зеленый
        'success_light': '#58d68d',
        'danger': '#e74c3c',       # Красный
        'danger_light': '#ec7063',
        'warning': '#f39c12',      # Оранжевый
        'warning_light': '#f8c471',
        'info': '#1abc9c',         # Бирюзовый
        'info_light': '#48c9b0',
        'light': '#ecf0f1',        # Светло-серый
        'light_dark': '#bdc3c7',
        'dark': '#2c3e50',         # Темный
        'dark_light': '#34495e',
        'white': '#ffffff',
        'gray': '#95a5a6',
        'gray_light': '#bdc3c7',
        'gray_dark': '#7f8c8d',
        'transparent': '#00000000',
        
        # Статусы заявок
        'status_new': '#3498db',
        'status_in_progress': '#f39c12',
        'status_waiting': '#e74c3c',
        'status_ready': '#2ecc71',
        
        # Приоритеты
        'priority_high': '#e74c3c',
        'priority_medium_high': '#e67e22',
        'priority_medium': '#f1c40f',
        'priority_medium_low': '#3498db',
        'priority_low': '#2ecc71',
    }
    
    # Градиенты
    GRADIENTS = {
        'primary': ['#2c3e50', '#4a6491'],
        'secondary': ['#3498db', '#2c3e50'],
        'success': ['#2ecc71', '#27ae60'],
        'danger': ['#e74c3c', '#c0392b'],
        'warning': ['#f39c12', '#d35400'],
    }
    
    # Тени
    SHADOWS = {
        'small': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        'medium': '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
        'large': '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
    }
    
    # Шрифты
    FONTS = {
        'title': ('Segoe UI', 20, 'bold'),
        'heading': ('Segoe UI', 16, 'bold'),
        'subheading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'body_bold': ('Segoe UI', 11, 'bold'),
        'small': ('Segoe UI', 9),
        'small_bold': ('Segoe UI', 9, 'bold'),
        'code': ('Consolas', 10),
        'icon': ('Segoe UI Symbol', 12),
    }
    
    @classmethod
    def configure_styles(cls):
        """Настройка стилей ttk"""
        style = ttk.Style()
        
        # Установка темы
        style.theme_use('clam')
        
        # Настройка базовых стилей
        style.configure('.', 
                       background=cls.COLORS['light'],
                       foreground=cls.COLORS['dark'],
                       font=cls.FONTS['body'])
        
        # ===== КНОПКИ =====
        # Основная кнопка
        style.configure('Primary.TButton',
            background=cls.COLORS['secondary'],
            foreground=cls.COLORS['white'],
            borderwidth=1,
            focusthickness=3,
            focuscolor=cls.COLORS['secondary_light'],
            font=cls.FONTS['body_bold'],
            padding=(20, 10)
        )
        style.map('Primary.TButton',
            background=[('active', cls.COLORS['secondary_light']),
                       ('disabled', cls.COLORS['gray_light'])],
            foreground=[('active', cls.COLORS['white']),
                       ('disabled', cls.COLORS['gray_dark'])]
        )
        
        # Успешная кнопка
        style.configure('Success.TButton',
            background=cls.COLORS['success'],
            foreground=cls.COLORS['white']
        )
        style.map('Success.TButton',
            background=[('active', cls.COLORS['success_light'])]
        )
        
        # Опасная кнопка
        style.configure('Danger.TButton',
            background=cls.COLORS['danger'],
            foreground=cls.COLORS['white']
        )
        style.map('Danger.TButton',
            background=[('active', cls.COLORS['danger_light'])]
        )
        
        # Предупреждающая кнопка
        style.configure('Warning.TButton',
            background=cls.COLORS['warning'],
            foreground=cls.COLORS['dark']
        )
        style.map('Warning.TButton',
            background=[('active', cls.COLORS['warning_light'])]
        )
        
        # Информационная кнопка
        style.configure('Info.TButton',
            background=cls.COLORS['info'],
            foreground=cls.COLORS['white']
        )
        style.map('Info.TButton',
            background=[('active', cls.COLORS['info_light'])]
        )
        
        # Плоская кнопка
        style.configure('Flat.TButton',
            background=cls.COLORS['transparent'],
            foreground=cls.COLORS['secondary'],
            borderwidth=0,
            padding=(10, 5)
        )
        style.map('Flat.TButton',
            background=[('active', cls.COLORS['light_dark'])]
        )
        
        # ===== ПОЛЯ ВВОДА =====
        style.configure('Modern.TEntry',
            fieldbackground=cls.COLORS['white'],
            foreground=cls.COLORS['dark'],
            bordercolor=cls.COLORS['gray_light'],
            lightcolor=cls.COLORS['gray_light'],
            darkcolor=cls.COLORS['gray_light'],
            padding=10,
            insertcolor=cls.COLORS['secondary'],
            insertwidth=2
        )
        style.map('Modern.TEntry',
            fieldbackground=[('focus', cls.COLORS['white']),
                           ('disabled', cls.COLORS['light'])],
            bordercolor=[('focus', cls.COLORS['secondary']),
                        ('disabled', cls.COLORS['gray'])]
        )
        
        # ===== МЕТКИ =====
        style.configure('Title.TLabel',
            font=cls.FONTS['title'],
            background=cls.COLORS['light'],
            foreground=cls.COLORS['primary']
        )
        
        style.configure('Heading.TLabel',
            font=cls.FONTS['heading'],
            background=cls.COLORS['light'],
            foreground=cls.COLORS['primary_light']
        )
        
        style.configure('Subheading.TLabel',
            font=cls.FONTS['subheading'],
            background=cls.COLORS['light'],
            foreground=cls.COLORS['dark']
        )
        
        style.configure('Body.TLabel',
            font=cls.FONTS['body']
        )
        
        style.configure('Small.TLabel',
            font=cls.FONTS['small'],
            foreground=cls.COLORS['gray_dark']
        )
        
        # ===== ФРЕЙМЫ =====
        style.configure('Card.TFrame',
            background=cls.COLORS['white'],
            relief='solid',
            borderwidth=1
        )
        
        style.configure('Panel.TFrame',
            background=cls.COLORS['primary_light'],
            relief='flat'
        )
        
        style.configure('Accent.TFrame',
            background=cls.COLORS['secondary'],
            relief='flat'
        )
        
        # ===== TREEVIEW =====
        style.configure('Modern.Treeview',
            background=cls.COLORS['white'],
            fieldbackground=cls.COLORS['white'],
            foreground=cls.COLORS['dark'],
            rowheight=35,
            font=cls.FONTS['body'],
            borderwidth=0
        )
        
        style.configure('Modern.Treeview.Heading',
            background=cls.COLORS['primary'],
            foreground=cls.COLORS['white'],
            font=cls.FONTS['body_bold'],
            relief='flat',
            padding=10
        )
        
        style.map('Modern.Treeview.Heading',
            background=[('active', cls.COLORS['primary_light'])]
        )
        
        # Чередование строк
        style.configure('Modern.Treeview',
            rowheight=35
        )
        
        style.map('Modern.Treeview',
            background=[('selected', cls.COLORS['secondary_light'])],
            foreground=[('selected', cls.COLORS['white'])]
        )
        
        # ===== NOTEBOOK =====
        style.configure('Modern.TNotebook',
            background=cls.COLORS['light'],
            tabmargins=[2, 5, 2, 0],
            borderwidth=0
        )
        
        style.configure('Modern.TNotebook.Tab',
            background=cls.COLORS['gray_light'],
            foreground=cls.COLORS['dark'],
            padding=[20, 10],
            font=cls.FONTS['body'],
            borderwidth=1
        )
        
        style.map('Modern.TNotebook.Tab',
            background=[('selected', cls.COLORS['white']),
                       ('active', cls.COLORS['light'])],
            foreground=[('selected', cls.COLORS['secondary']),
                       ('active', cls.COLORS['dark'])]
        )
        
        # ===== SCROLLBAR =====
        style.configure('Modern.Vertical.TScrollbar',
            background=cls.COLORS['light'],
            darkcolor=cls.COLORS['gray_light'],
            lightcolor=cls.COLORS['gray_light'],
            troughcolor=cls.COLORS['light'],
            bordercolor=cls.COLORS['light'],
            arrowcolor=cls.COLORS['dark'],
            gripcount=0
        )
        
        style.map('Modern.Vertical.TScrollbar',
            background=[('active', cls.COLORS['gray'])],
            darkcolor=[('active', cls.COLORS['gray'])],
            lightcolor=[('active', cls.COLORS['gray'])]
        )
        
        style.configure('Modern.Horizontal.TScrollbar',
            background=cls.COLORS['light'],
            darkcolor=cls.COLORS['gray_light'],
            lightcolor=cls.COLORS['gray_light'],
            troughcolor=cls.COLORS['light'],
            bordercolor=cls.COLORS['light'],
            arrowcolor=cls.COLORS['dark']
        )
        
        # ===== COMBOBOX =====
        style.configure('Modern.TCombobox',
            fieldbackground=cls.COLORS['white'],
            background=cls.COLORS['white'],
            foreground=cls.COLORS['dark'],
            selectbackground=cls.COLORS['secondary_light'],
            selectforeground=cls.COLORS['white'],
            padding=8,
            arrowsize=15
        )
        
        style.map('Modern.TCombobox',
            fieldbackground=[('readonly', cls.COLORS['white'])],
            selectbackground=[('readonly', cls.COLORS['secondary'])]
        )
        
        # ===== PROGRESSBAR =====
        style.configure('Modern.Horizontal.TProgressbar',
            background=cls.COLORS['secondary'],
            troughcolor=cls.COLORS['light'],
            bordercolor=cls.COLORS['light'],
            lightcolor=cls.COLORS['secondary'],
            darkcolor=cls.COLORS['secondary'],
            thickness=20
        )
        
        # ===== SEPARATOR =====
        style.configure('Modern.TSeparator',
            background=cls.COLORS['gray_light']
        )
        
        # ===== CHECKBUTTON =====
        style.configure('Modern.TCheckbutton',
            background=cls.COLORS['light'],
            foreground=cls.COLORS['dark'],
            indicatormargin=[10, 10, 10, 10]
        )
        
        style.map('Modern.TCheckbutton',
            background=[('active', cls.COLORS['light'])]
        )
        
        # ===== RADIOBUTTON =====
        style.configure('Modern.TRadiobutton',
            background=cls.COLORS['light'],
            foreground=cls.COLORS['dark']
        )
        
        style.map('Modern.TRadiobutton',
            background=[('active', cls.COLORS['light'])]
        )
    
    @classmethod
    def create_gradient_canvas(cls, parent, colors, width, height, direction='horizontal'):
        """Создание канваса с градиентом"""
        canvas = tk.Canvas(parent, width=width, height=height, 
                          highlightthickness=0, borderwidth=0)
        
        if direction == 'horizontal':
            for i in range(width):
                ratio = i / width
                r = int((1 - ratio) * colors[0][0] + ratio * colors[1][0])
                g = int((1 - ratio) * colors[0][1] + ratio * colors[1][1])
                b = int((1 - ratio) * colors[0][2] + ratio * colors[1][2])
                color = f'#{r:02x}{g:02x}{b:02x}'
                canvas.create_line(i, 0, i, height, fill=color)
        else:
            for i in range(height):
                ratio = i / height
                r = int((1 - ratio) * colors[0][0] + ratio * colors[1][0])
                g = int((1 - ratio) * colors[0][1] + ratio * colors[1][1])
                b = int((1 - ratio) * colors[0][2] + ratio * colors[1][2])
                color = f'#{r:02x}{g:02x}{b:02x}'
                canvas.create_line(0, i, width, i, fill=color)
        
        return canvas
    
    @classmethod
    def hex_to_rgb(cls, hex_color):
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @classmethod
    def rgb_to_hex(cls, rgb):
        """Конвертация RGB в HEX"""
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    @classmethod
    def lighten_color(cls, hex_color, factor=0.2):
        """Осветление цвета"""
        rgb = cls.hex_to_rgb(hex_color)
        r = min(255, int(rgb[0] + (255 - rgb[0]) * factor))
        g = min(255, int(rgb[1] + (255 - rgb[1]) * factor))
        b = min(255, int(rgb[2] + (255 - rgb[2]) * factor))
        return cls.rgb_to_hex((r, g, b))
    
    @classmethod
    def darken_color(cls, hex_color, factor=0.2):
        """Затемнение цвета"""
        rgb = cls.hex_to_rgb(hex_color)
        r = max(0, int(rgb[0] * (1 - factor)))
        g = max(0, int(rgb[1] * (1 - factor)))
        b = max(0, int(rgb[2] * (1 - factor)))
        return cls.rgb_to_hex((r, g, b))

class Theme:
    """Управление темами"""
    
    @staticmethod
    def apply_light_theme(root):
        """Применение светлой темы"""
        root.configure(bg=StyleManager.COLORS['light'])
    
    @staticmethod
    def apply_dark_theme(root):
        """Применение темной темы"""
        # Обновляем цвета для темной темы
        dark_colors = {
            'primary': '#34495e',
            'primary_light': '#2c3e50',
            'secondary': '#3498db',
            'light': '#2c3e50',
            'dark': '#ecf0f1',
            'white': '#34495e',
            'gray': '#7f8c8d',
            'gray_light': '#95a5a6',
            'gray_dark': '#bdc3c7'
        }
        
        for key, value in dark_colors.items():
            StyleManager.COLORS[key] = value
        
        root.configure(bg=StyleManager.COLORS['light'])
        StyleManager.configure_styles()
    
    @staticmethod
    def apply_blue_theme(root):
        """Применение синей темы"""
        blue_colors = {
            'primary': '#2980b9',
            'primary_light': '#3498db',
            'secondary': '#2c3e50',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        for key, value in blue_colors.items():
            StyleManager.COLORS[key] = value
        
        root.configure(bg=StyleManager.COLORS['light'])
        StyleManager.configure_styles()
    
    @staticmethod
    def apply_green_theme(root):
        """Применение зеленой темы"""
        green_colors = {
            'primary': '#27ae60',
            'primary_light': '#2ecc71',
            'secondary': '#2c3e50',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        for key, value in green_colors.items():
            StyleManager.COLORS[key] = value
        
        root.configure(bg=StyleManager.COLORS['light'])
        StyleManager.configure_styles()

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Создание прямоугольника со скругленными углами"""
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    
    return canvas.create_polygon(points, **kwargs, smooth=True)

def create_shadow(canvas, x1, y1, x2, y2, radius=25, color='#000000', offset=2, opacity=0.1):
    """Создание тени для элемента"""
    shadow_color = StyleManager.rgb_to_hex(
        tuple(int(255 * (1 - opacity) + c * opacity) for c in StyleManager.hex_to_rgb(color))
    )
    
    return create_rounded_rectangle(canvas, 
                                   x1+offset, y1+offset, 
                                   x2+offset, y2+offset, 
                                   radius, 
                                   fill=shadow_color, 
                                   outline='')

def add_hover_effect(widget, normal_bg, hover_bg):
    """Добавление эффекта наведения"""
    def on_enter(e):
        widget.configure(background=hover_bg)
    
    def on_leave(e):
        widget.configure(background=normal_bg)
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)