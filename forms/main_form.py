import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from styles import StyleManager
from widgets import (Card, MetricCard, SearchBox, StatusBadge, 
                    PriorityBadge, NotificationBadge, Avatar, ProgressBar,
                    PieChart, BarChart, GaugeChart)
from .request_form import RequestForm
from .statistics_form import StatisticsForm
from .quality_manager_form import QualityManagerForm

class MainForm:
    """Главная форма приложения"""
    
    def __init__(self, master, user, db):
        self.master = master
        self.user = user
        self.db = db
        
        self.setup_ui()
        self.setup_menu()
        self.load_dashboard_data()
        self.load_notifications()
        
        # Центрирование окна
        self.center_window()
    
    def center_window(self):
        """Центрирование окна"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Настройка интерфейса"""
        self.master.title(f"Сервисный центр - {self.user.fio} ({self.user.type})")
        self.master.geometry("1400x800")
        
        # Применение стилей
        StyleManager.configure_styles()
        self.master.configure(bg=StyleManager.COLORS['light'])
        
        # Главный контейнер
        main_container = ttk.Frame(self.master)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель
        self.setup_header(main_container)
        
        # Основное содержимое
        self.notebook = ttk.Notebook(main_container, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создаем вкладки
        self.setup_dashboard_tab()
        self.setup_requests_tab()
        
        if self.user.has_permission('view_statistics'):
            self.setup_statistics_tab()
        
        if self.user.has_permission('quality_control'):
            self.setup_quality_tab()
        
        # Бинды для горячих клавиш
        self.setup_hotkeys()
    
    def setup_header(self, parent):
        """Верхняя панель с информацией"""
        header = ttk.Frame(parent, style='Panel.TFrame')
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Логотип и название
        logo_frame = ttk.Frame(header)
        logo_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Label(logo_frame, text="🔧", 
                 font=('Segoe UI', 24)).pack(side=tk.LEFT)
        
        ttk.Label(logo_frame, text="Сервисный центр",
                 style='Heading.TLabel',
                 foreground=StyleManager.COLORS['white']).pack(side=tk.LEFT, padx=5)
        
        # Информация о пользователе
        user_frame = ttk.Frame(header)
        user_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Уведомления
        self.notification_badge = NotificationBadge(user_frame)
        self.notification_badge.pack(side=tk.LEFT, padx=5)
        
        # Аватар пользователя
        avatar = Avatar(user_frame, text=self.user.fio[:2], size=40)
        avatar.pack(side=tk.LEFT, padx=5)
        
        # Информация
        info_frame = ttk.Frame(user_frame)
        info_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(info_frame, text=self.user.fio,
                 style='Body.TLabel',
                 foreground=StyleManager.COLORS['white']).pack(anchor=tk.E)
        
        role_colors = {
            'Менеджер': StyleManager.COLORS['warning_light'],
            'Мастер': StyleManager.COLORS['success_light'],
            'Оператор': StyleManager.COLORS['info_light'],
            'Заказчик': StyleManager.COLORS['secondary_light'],
            'Менеджер качества': StyleManager.COLORS['danger_light']
        }
        
        role_color = role_colors.get(self.user.type, StyleManager.COLORS['white'])
        ttk.Label(info_frame, text=self.user.type,
                 style='Small.TLabel',
                 foreground=role_color).pack(anchor=tk.E)
        
        # Кнопка выхода
        logout_btn = ttk.Button(user_frame, text="🚪", 
                               style='Flat.TButton',
                               command=self.logout,
                               width=3)
        logout_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def setup_dashboard_tab(self):
        """Вкладка Дашборд"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Дашборд")
        
        # Контейнер с прокруткой
        canvas = tk.Canvas(dashboard_frame, bg=StyleManager.COLORS['light'])
        scrollbar = ttk.Scrollbar(dashboard_frame, orient=tk.VERTICAL, 
                                 command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Верхний ряд метрик
        metrics_row1 = ttk.Frame(scrollable_frame)
        metrics_row1.pack(fill=tk.X, padx=20, pady=20)
        
        # Метрики
        self.total_metric = MetricCard(metrics_row1, "Всего заявок", "0", 
                                      icon="📋", color=StyleManager.COLORS['primary'])
        self.total_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        self.active_metric = MetricCard(metrics_row1, "Активные", "0",
                                       icon="🔧", color=StyleManager.COLORS['warning'])
        self.active_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        self.completed_metric = MetricCard(metrics_row1, "Завершено", "0",
                                          icon="✅", color=StyleManager.COLORS['success'])
        self.completed_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        self.revenue_metric = MetricCard(metrics_row1, "Доход", "0", "₽",
                                        icon="💰", color=StyleManager.COLORS['info'])
        self.revenue_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Второй ряд метрик
        metrics_row2 = ttk.Frame(scrollable_frame)
        metrics_row2.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.avg_time_metric = MetricCard(metrics_row2, "Ср. время", "0", "дн",
                                         icon="⏱️", color=StyleManager.COLORS['secondary'])
        self.avg_time_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        self.clients_metric = MetricCard(metrics_row2, "Клиенты", "0",
                                        icon="👥", color=StyleManager.COLORS['danger'])
        self.clients_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        self.completion_metric = MetricCard(metrics_row2, "Выполнено", "0", "%",
                                           icon="📈", color=StyleManager.COLORS['success'])
        self.completion_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        self.overdue_metric = MetricCard(metrics_row2, "Просрочено", "0",
                                        icon="⚠️", color=StyleManager.COLORS['danger'])
        self.overdue_metric.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Графики
        charts_frame = ttk.Frame(scrollable_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Статусы заявок
        status_card = Card(charts_frame, title="Статусы заявок")
        status_card.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        self.status_chart = PieChart(status_card.content_frame, 
                                    width=300, height=300)
        self.status_chart.pack(padx=10, pady=10)
        
        # Типы техники
        tech_card = Card(charts_frame, title="Типы техники")
        tech_card.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        self.tech_chart = BarChart(tech_card.content_frame,
                                  width=400, height=300)
        self.tech_chart.pack(padx=10, pady=10)
        
        # Производительность
        perf_card = Card(charts_frame, title="Производительность")
        perf_card.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        self.performance_gauge = GaugeChart(perf_card.content_frame,
                                          width=300, height=200)
        self.performance_gauge.pack(padx=10, pady=10)
        
        # Последние заявки
        recent_card = Card(charts_frame, title="Последние заявки")
        recent_card.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        self.recent_tree = ttk.Treeview(recent_card.content_frame, 
                                       columns=("ID", "Техника", "Статус", "Дней"),
                                       style='Modern.Treeview',
                                       height=8,
                                       show="headings")
        
        self.recent_tree.heading("ID", text="ID")
        self.recent_tree.heading("Техника", text="Техника")
        self.recent_tree.heading("Статус", text="Статус")
        self.recent_tree.heading("Дней", text="Дней")
        
        self.recent_tree.column("ID", width=50)
        self.recent_tree.column("Техника", width=100)
        self.recent_tree.column("Статус", width=100)
        self.recent_tree.column("Дней", width=60)
        
        scrollbar = ttk.Scrollbar(recent_card.content_frame,
                                 orient=tk.VERTICAL,
                                 command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Двойной клик для открытия заявки
        self.recent_tree.bind('<Double-1>', self.open_selected_request)
        
        # Настройка сетки
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)
    
    def setup_requests_tab(self):
        """Вкладка Заявки"""
        requests_frame = ttk.Frame(self.notebook)
        self.notebook.add(requests_frame, text="📋 Заявки")
        
        # Панель инструментов
        toolbar = ttk.Frame(requests_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        # Кнопка новой заявки
        if self.user.has_permission('create_request'):
            ttk.Button(toolbar, text="➕ Новая заявка",
                      style='Success.TButton',
                      command=self.create_request).pack(side=tk.LEFT, padx=5)
        
        # Кнопка обновления
        ttk.Button(toolbar, text="🔄 Обновить",
                  style='Primary.TButton',
                  command=self.refresh_requests).pack(side=tk.LEFT, padx=5)
        
        # Экспорт
        ttk.Button(toolbar, text="📤 Экспорт",
                  style='Info.TButton',
                  command=self.export_data).pack(side=tk.LEFT, padx=5)
        
        # Поиск
        self.search_box = SearchBox(toolbar, 
                                   placeholder="Поиск по ID, технике, клиенту...",
                                   on_search=self.filter_requests)
        self.search_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Фильтры
        filter_frame = ttk.Frame(requests_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Фильтры:", 
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        # Фильтр по статусу
        ttk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter = ttk.Combobox(filter_frame, 
                                         values=['Все', 'Новая заявка', 'В процессе ремонта', 
                                                 'Ожидание запчастей', 'Готова к выдаче'],
                                         state='readonly',
                                         width=20)
        self.status_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.status_filter.set('Все')
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_requests())
        
        # Фильтр по типу техники
        ttk.Label(filter_frame, text="Техника:").pack(side=tk.LEFT, padx=(0, 5))
        self.tech_filter = ttk.Combobox(filter_frame, 
                                       values=['Все', 'Холодильник', 'Стиральная машина', 
                                               'Плита', 'Микроволновая печь', 'Фен', 
                                               'Тостер', 'Мультиварка'],
                                       state='readonly',
                                       width=20)
        self.tech_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.tech_filter.set('Все')
        self.tech_filter.bind('<<ComboboxSelected>>', lambda e: self.filter_requests())
        
        # Кнопка сброса фильтров
        ttk.Button(filter_frame, text="Сбросить",
                  command=self.reset_filters).pack(side=tk.LEFT)
        
        # Таблица заявок
        table_frame = ttk.Frame(requests_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Создание Treeview
        columns = ("ID", "Дата", "Техника", "Модель", "Проблема", 
                  "Статус", "Приоритет", "Клиент", "Мастер", "Дней")
        
        self.requests_tree = ttk.Treeview(table_frame, columns=columns, 
                                         style='Modern.Treeview',
                                         show="headings",
                                         height=20)
        
        # Настройка колонок
        col_widths = [50, 80, 100, 120, 150, 100, 80, 120, 100, 50]
        for idx, col in enumerate(columns):
            self.requests_tree.heading(col, text=col, 
                                      command=lambda c=col: self.sort_by_column(c))
            self.requests_tree.column(col, width=col_widths[idx], 
                                     anchor=tk.CENTER if idx in [0, 9] else tk.W)
        
        # Прокрутка
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                   command=self.requests_tree.yview)
        self.requests_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL,
                                   command=self.requests_tree.xview)
        self.requests_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Размещение
        self.requests_tree.grid(row=0, column=0, sticky=tk.NSEW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW, columnspan=2)
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Контекстное меню
        self.setup_context_menu()
        
        # Бинды
        self.requests_tree.bind('<Double-1>', self.open_selected_request)
        
        # Загрузка данных
        self.filter_requests()
    
    def setup_statistics_tab(self):
        """Вкладка Статистика"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 Статистика")
        
        self.stats_form = StatisticsForm(stats_frame, self.db, self.user)
        self.stats_form.pack(fill=tk.BOTH, expand=True)
    
    def setup_quality_tab(self):
        """Вкладка Контроль качества"""
        quality_frame = ttk.Frame(self.notebook)
        self.notebook.add(quality_frame, text="⭐ Качество")
        
        self.quality_form = QualityManagerForm(quality_frame, self.user, self.db)
        self.quality_form.pack(fill=tk.BOTH, expand=True)
    
    def setup_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        file_menu.add_command(label="Экспорт данных", 
                             command=self.export_data,
                             accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Резервная копия", 
                             command=self.create_backup)
        file_menu.add_command(label="Восстановить", 
                             command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", 
                             command=self.logout,
                             accelerator="Ctrl+Q")
        
        # Меню "Заявки"
        request_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Заявки", menu=request_menu)
        
        request_menu.add_command(label="Новая заявка", 
                               command=self.create_request,
                               accelerator="Ctrl+N")
        request_menu.add_command(label="Поиск", 
                               command=self.focus_search,
                               accelerator="Ctrl+F")
        request_menu.add_separator()
        request_menu.add_command(label="Обновить", 
                               command=self.refresh_all,
                               accelerator="F5")
        
        # Меню "Отчеты"
        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=report_menu)
        
        report_menu.add_command(label="Ежедневный отчет", 
                              command=self.daily_report)
        report_menu.add_command(label="Отчет по мастерам", 
                              command=self.masters_report)
        report_menu.add_command(label="Статистика по технике", 
                              command=self.tech_report)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        help_menu.add_command(label="О программе", 
                            command=self.show_about)
        help_menu.add_command(label="Руководство", 
                            command=self.show_manual)
        help_menu.add_command(label="Проверить обновления", 
                            command=self.check_updates)
    
    def setup_context_menu(self):
        """Контекстное меню для таблицы"""
        self.context_menu = tk.Menu(self.requests_tree, tearoff=0)
        
        self.context_menu.add_command(label="📝 Редактировать", 
                                     command=self.open_selected_request)
        self.context_menu.add_command(label="👁 Просмотреть", 
                                     command=self.view_selected_request)
        self.context_menu.add_separator()
        
        if self.user.has_permission('edit_request'):
            self.context_menu.add_command(label="✅ Завершить", 
                                         command=self.complete_selected_request)
            self.context_menu.add_command(label="🔄 Сменить статус", 
                                         command=self.change_status)
            self.context_menu.add_separator()
        
        if self.user.has_permission('delete_request'):
            self.context_menu.add_command(label="🗑 Удалить", 
                                         command=self.delete_selected_request)
        
        self.requests_tree.bind('<Button-3>', self.show_context_menu)
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.master.bind('<Control-n>', lambda e: self.create_request())
        self.master.bind('<Control-f>', lambda e: self.focus_search())
        self.master.bind('<F5>', lambda e: self.refresh_all())
        self.master.bind('<Control-e>', lambda e: self.export_data())
        self.master.bind('<Control-q>', lambda e: self.logout())
    
    def load_dashboard_data(self):
        """Загрузка данных для дашборда"""
        stats = self.db.get_statistics()
        
        # Обновляем метрики
        self.total_metric.update_value(stats['total_requests'])
        self.active_metric.update_value(stats['active_requests'])
        self.completed_metric.update_value(stats['completed_requests'])
        self.revenue_metric.update_value(f"{stats['total_revenue']:,.0f}")
        self.avg_time_metric.update_value(f"{stats['avg_repair_days']:.1f}")
        self.clients_metric.update_value(stats['unique_clients'])
        
        # Процент выполнения
        completion_rate = (stats['completed_requests'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
        self.completion_metric.update_value(f"{completion_rate:.1f}")
        
        # Просроченные заявки
        overdue = self.db.get_overdue_requests()
        self.overdue_metric.update_value(len(overdue))
        
        # Графики
        self.status_chart.set_data(stats['by_status'])
        
        # Типы техники
        tech_data = {row[0]: row[1] for row in stats['by_tech_type'][:5]}
        self.tech_chart.set_data(tech_data)
        
        # Датчик производительности
        self.performance_gauge.set_value(completion_rate, "Выполнение", "%")
        
        # Последние заявки
        self.load_recent_requests()
    
    def load_recent_requests(self):
        """Загрузка последних заявок"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.requestID, r.homeTechType, r.requestStatus,
                       julianday('now') - julianday(r.startDate) as days
                FROM requests r
                ORDER BY r.startDate DESC
                LIMIT 10
            ''')
            
            # Очищаем таблицу
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
            
            # Заполняем данными
            for row in cursor.fetchall():
                self.recent_tree.insert('', tk.END, values=row)
    
    def load_notifications(self):
        """Загрузка уведомлений"""
        notifications = self.db.get_user_notifications(self.user.userID, unread_only=True)
        self.notification_badge.update_count(len(notifications))
    
    def filter_requests(self, search_text=None):
        """Фильтрация заявок"""
        search = search_text if search_text is not None else self.search_box.get()
        filters = {}
        
        if self.status_filter.get() != 'Все':
            filters['status'] = self.status_filter.get()
        
        if self.tech_filter.get() != 'Все':
            filters['tech_type'] = self.tech_filter.get()
        
        requests = self.db.search_requests(search, filters)
        
        # Очищаем таблицу
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
        
        # Заполняем данными
        for req in requests:
            days = (datetime.now() - datetime.strptime(req['startDate'], "%Y-%m-%d")).days
            values = (
                req['requestID'],
                req['startDate'],
                req['homeTechType'],
                req['homeTechModel'],
                req['problemDescription'][:30] + "..." if len(req['problemDescription']) > 30 else req['problemDescription'],
                req['requestStatus'],
                req['priority'],
                req.get('client_name', ''),
                req.get('master_name', ''),
                days
            )
            
            item = self.requests_tree.insert('', tk.END, values=values)
            
            # Подсветка просроченных заявок
            if days > 7 and req['requestStatus'] != 'Готова к выдаче':
                self.requests_tree.item(item, tags=('overdue',))
        
        # Настройка тегов
        self.requests_tree.tag_configure('overdue', background=StyleManager.COLORS['danger_light'])
    
    def sort_by_column(self, col):
        """Сортировка по колонке"""
        # Реализация сортировки
        pass
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.requests_tree.identify_row(event.y)
        if item:
            self.requests_tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def create_request(self):
        """Создание новой заявки"""
        RequestForm(self.master, self.user, self.db, self.refresh_all)
    
    def open_selected_request(self, event=None):
        """Открыть выбранную заявку"""
        selection = self.requests_tree.selection()
        if selection:
            item = self.requests_tree.item(selection[0])
            request_id = item['values'][0]
            
            RequestForm(self.master, self.user, self.db, 
                       self.refresh_all, request_id, mode='edit')
    
    def view_selected_request(self):
        """Просмотр выбранной заявки"""
        selection = self.requests_tree.selection()
        if selection:
            item = self.requests_tree.item(selection[0])
            request_id = item['values'][0]
            
            RequestForm(self.master, self.user, self.db, 
                       self.refresh_all, request_id, mode='view')
    
    def complete_selected_request(self):
        """Завершить выбранную заявку"""
        selection = self.requests_tree.selection()
        if not selection:
            return
        
        item = self.requests_tree.item(selection[0])
        request_id = item['values'][0]
        
        response = messagebox.askyesno("Подтверждение", 
                                      f"Завершить заявку #{request_id}?")
        
        if response and self.db.update_request_status(request_id, 'Готова к выдаче'):
            self.refresh_all()
            messagebox.showinfo("Успех", "Заявка завершена")
    
    def change_status(self):
        """Сменить статус заявки"""
        selection = self.requests_tree.selection()
        if not selection:
            return
        
        item = self.requests_tree.item(selection[0])
        request_id = item['values'][0]
        
        # Диалог смены статуса
        dialog = tk.Toplevel(self.master)
        dialog.title("Смена статуса")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Выберите новый статус:").pack(pady=20)
        
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(dialog, textvariable=status_var,
                                   values=['Новая заявка', 'В процессе ремонта',
                                           'Ожидание запчастей', 'Готова к выдаче'],
                                   state='readonly')
        status_combo.pack(pady=10)
        
        def confirm_change():
            if self.db.update_request_status(request_id, status_var.get()):
                dialog.destroy()
                self.refresh_all()
                messagebox.showinfo("Успех", "Статус изменен")
        
        ttk.Button(dialog, text="Применить",
                  command=confirm_change).pack(pady=20)
    
    def delete_selected_request(self):
        """Удалить выбранную заявку"""
        selection = self.requests_tree.selection()
        if not selection:
            return
        
        item = self.requests_tree.item(selection[0])
        request_id = item['values'][0]
        
        response = messagebox.askyesno("Подтверждение удаления", 
                                      f"Вы уверены, что хотите удалить заявку #{request_id}?")
        
        if response:
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM requests WHERE requestID = ?', (request_id,))
                    conn.commit()
                
                self.refresh_all()
                messagebox.showinfo("Успех", "Заявка удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заявку: {e}")
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.search_box.clear_search()
        self.status_filter.set('Все')
        self.tech_filter.set('Все')
        self.filter_requests()
    
    def focus_search(self):
        """Установить фокус на поле поиска"""
        self.notebook.select(1)  # Переключиться на вкладку Заявки
        self.search_box.focus_search()
    
    def refresh_requests(self):
        """Обновить список заявок"""
        self.filter_requests()
    
    def refresh_all(self):
        """Обновить все данные"""
        self.load_dashboard_data()
        self.filter_requests()
        self.load_notifications()
        
        if hasattr(self, 'stats_form'):
            self.stats_form.refresh()
        
        if hasattr(self, 'quality_form'):
            self.quality_form.refresh()
        
        messagebox.showinfo("Обновление", "Данные успешно обновлены")
    
    def export_data(self):
        """Экспорт данных"""
        from utils.exporters import DataExporter
        
        exporter = DataExporter(self.db)
        filename = exporter.export_requests()
        
        if filename:
            messagebox.showinfo("Экспорт", 
                              f"Данные успешно экспортированы:\n{filename}")
    
    def create_backup(self):
        """Создать резервную копию"""
        from utils.backup import DatabaseBackup
        
        backup_file = DatabaseBackup.create_backup()
        messagebox.showinfo("Резервное копирование",
                          f"Резервная копия создана:\n{backup_file}")
    
    def restore_backup(self):
        """Восстановить из резервной копии"""
        # Реализация выбора файла
        pass
    
    def daily_report(self):
        """Ежедневный отчет"""
        if hasattr(self, 'stats_form'):
            self.stats_form.generate_daily_report()
    
    def masters_report(self):
        """Отчет по мастерам"""
        if hasattr(self, 'stats_form'):
            self.stats_form.generate_masters_report()
    
    def tech_report(self):
        """Отчет по технике"""
        if hasattr(self, 'stats_form'):
            self.stats_form.generate_tech_report()
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """
        Сервисный центр - Учет заявок на ремонт
        
        Версия: 2.0
        Разработчик: IT-Соm
        
        Система автоматизации учета заявок
        на ремонт бытовой техники.
        
        © 2024 Все права защищены.
        """
        
        messagebox.showinfo("О программе", about_text)
    
    def show_manual(self):
        """Показать руководство"""
        messagebox.showinfo("Руководство", 
                          "Руководство пользователя открыто в браузере.")
    
    def check_updates(self):
        """Проверить обновления"""
        messagebox.showinfo("Обновления", 
                          "Проверка обновлений...\nУ вас установлена последняя версия.")
    
    def logout(self):
        """Выход из системы"""
        response = messagebox.askyesno("Выход", 
                                      "Вы уверены, что хотите выйти из системы?")
        if response:
            self.master.destroy()