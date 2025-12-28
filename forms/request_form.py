import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from styles import StyleManager
from widgets import Card, StatusBadge, PriorityBadge, ProgressBar, Avatar
from utils.generators import QRCodeGenerator
from utils.validators import Validators
from PIL import Image, ImageTk

class RequestForm:
    """Форма работы с заявкой"""
    
    def __init__(self, parent, user, db, callback, request_id=None, mode='create'):
        self.parent = parent
        self.user = user
        self.db = db
        self.callback = callback
        self.request_id = request_id
        self.mode = mode  # 'create', 'edit', 'view'
        
        self.window = tk.Toplevel(parent)
        self.window.title(self._get_title())
        self.window.geometry("1000x700")
        
        # Центрирование
        self.center_window()
        
        self.load_data()
        self.setup_ui()
        
        if mode == 'view':
            self.set_readonly()
    
    def center_window(self):
        """Центрирование окна"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _get_title(self):
        """Получить заголовок окна"""
        titles = {
            'create': '➕ Новая заявка',
            'edit': f'✏️ Редактирование заявки #{self.request_id}',
            'view': f'👁 Просмотр заявки #{self.request_id}'
        }
        return titles.get(self.mode, 'Заявка')
    
    def load_data(self):
        """Загрузка данных заявки"""
        if self.request_id:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Загрузка данных заявки
                cursor.execute('''
                    SELECT r.*, c.fio as client_name, c.phone as client_phone,
                           m.fio as master_name, qm.fio as qm_name
                    FROM requests r
                    LEFT JOIN users c ON r.clientID = c.userID
                    LEFT JOIN users m ON r.masterID = m.userID
                    LEFT JOIN users qm ON r.qualityManagerID = qm.userID
                    WHERE r.requestID = ?
                ''', (self.request_id,))
                
                row = cursor.fetchone()
                if row:
                    self.request_data = dict(row)
                    
                    # Загрузка комментариев
                    cursor.execute('''
                        SELECT c.*, u.fio as author_name
                        FROM comments c
                        LEFT JOIN users u ON c.masterID = u.userID
                        WHERE c.requestID = ?
                        ORDER BY c.timestamp DESC
                    ''', (self.request_id,))
                    
                    self.comments = [dict(row) for row in cursor.fetchall()]
                    
                    # Загрузка списка мастеров
                    cursor.execute('''
                        SELECT userID, fio FROM users 
                        WHERE type = 'Мастер' AND is_active = 1
                        ORDER BY fio
                    ''')
                    
                    self.masters = cursor.fetchall()
                    
                    # Загрузка списка клиентов
                    cursor.execute('''
                        SELECT userID, fio, phone FROM users 
                        WHERE type = 'Заказчик' AND is_active = 1
                        ORDER BY fio
                    ''')
                    
                    self.clients = cursor.fetchall()
                    
                    # Загрузка запчастей
                    cursor.execute('''
                        SELECT p.* FROM parts p
                        JOIN request_parts rp ON p.partID = rp.partID
                        WHERE rp.requestID = ?
                    ''', (self.request_id,))
                    
                    self.parts = [dict(row) for row in cursor.fetchall()]
                else:
                    messagebox.showerror("Ошибка", "Заявка не найдена")
                    self.window.destroy()
        else:
            # Для новой заявки загружаем только списки
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT userID, fio FROM users 
                    WHERE type = 'Мастер' AND is_active = 1
                    ORDER BY fio
                ''')
                self.masters = cursor.fetchall()
                
                cursor.execute('''
                    SELECT userID, fio, phone FROM users 
                    WHERE type = 'Заказчик' AND is_active = 1
                    ORDER BY fio
                ''')
                self.clients = cursor.fetchall()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        self.window.configure(bg=StyleManager.COLORS['light'])
        
        # Основной контейнер
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook для вкладок
        notebook = ttk.Notebook(main_container, style='Modern.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        self.setup_main_tab(notebook)
        self.setup_comments_tab(notebook)
        self.setup_parts_tab(notebook)
        
        if self.mode != 'create' and self.request_data and self.request_data['requestStatus'] == 'Готова к выдаче':
            self.setup_feedback_tab(notebook)
        
        # Панель кнопок
        self.setup_button_panel(main_container)
    
    def setup_main_tab(self, notebook):
        """Настройка вкладки основной информации"""
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="📋 Основное")
        
        # Контейнер с прокруткой
        canvas = tk.Canvas(main_frame, bg=StyleManager.COLORS['light'])
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
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
        
        # Форма с полями
        form_card = Card(scrollable_frame, title="Информация о заявке", padding=20)
        form_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Прогресс выполнения
        if self.mode != 'create':
            progress_frame = ttk.Frame(form_card.content_frame)
            progress_frame.pack(fill=tk.X, pady=(0, 20))
            
            ttk.Label(progress_frame, text="Прогресс выполнения:", 
                     style='Subheading.TLabel').pack(anchor=tk.W)
            
            progress_value = 0
            if self.request_data:
                status_progress = {
                    'Новая заявка': 25,
                    'Ожидание запчастей': 50,
                    'В процессе ремонта': 75,
                    'Готова к выдаче': 100
                }
                progress_value = status_progress.get(self.request_data['requestStatus'], 0)
            
            self.progress_bar = ProgressBar(progress_frame, width=400, height=20, 
                                           value=progress_value)
            self.progress_bar.pack(pady=5)
        
        # Основные поля
        fields_frame = ttk.Frame(form_card.content_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Статус заявки
        if self.mode != 'create':
            ttk.Label(fields_frame, text="Статус заявки:", 
                     style='Body.TLabel').grid(row=row, column=0, 
                                              sticky=tk.W, pady=(0, 10))
            
            if self.mode == 'view':
                status_frame = ttk.Frame(fields_frame)
                status_frame.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
                StatusBadge(status_frame, self.request_data['requestStatus'], 
                           size='medium').pack()
            else:
                self.status_var = tk.StringVar(value=self.request_data['requestStatus'])
                status_combo = ttk.Combobox(fields_frame, textvariable=self.status_var,
                                           values=['Новая заявка', 'В процессе ремонта',
                                                   'Ожидание запчастей', 'Готова к выдаче'],
                                           state='readonly',
                                           width=30)
                status_combo.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
            
            row += 1
        
        # Приоритет
        ttk.Label(fields_frame, text="Приоритет:", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.W, pady=(0, 10))
        
        if self.mode == 'view' and self.request_data:
            priority_frame = ttk.Frame(fields_frame)
            priority_frame.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
            PriorityBadge(priority_frame, self.request_data['priority'], 
                         size='medium').pack()
        else:
            self.priority_var = tk.IntVar(value=self.request_data.get('priority', 3) if self.request_data else 3)
            priority_combo = ttk.Combobox(fields_frame, textvariable=self.priority_var,
                                         values=[(1, 'Высокий'), (2, 'Выше среднего'), 
                                                (3, 'Средний'), (4, 'Ниже среднего'), 
                                                (5, 'Низкий')],
                                         state='readonly',
                                         width=30)
            priority_combo.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        row += 1
        
        # Тип техники
        ttk.Label(fields_frame, text="Тип техники:*", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.W, pady=(0, 10))
        
        self.tech_type_var = tk.StringVar()
        tech_type_combo = ttk.Combobox(fields_frame, textvariable=self.tech_type_var,
                                      values=['Холодильник', 'Стиральная машина', 
                                              'Плита', 'Микроволновая печь', 
                                              'Фен', 'Тостер', 'Мультиварка', 'Другое'],
                                      state='normal',
                                      width=30)
        tech_type_combo.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        if self.request_data:
            tech_type_combo.set(self.request_data['homeTechType'])
        
        row += 1
        
        # Модель техники
        ttk.Label(fields_frame, text="Модель техники:*", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.W, pady=(0, 10))
        
        self.model_var = tk.StringVar()
        model_entry = ttk.Entry(fields_frame, textvariable=self.model_var,
                               style='Modern.TEntry', width=33)
        model_entry.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        if self.request_data:
            model_entry.insert(0, self.request_data['homeTechModel'])
        
        row += 1
        
        # Описание проблемы
        ttk.Label(fields_frame, text="Описание проблемы:*", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.NW, pady=(0, 10))
        
        self.problem_text = tk.Text(fields_frame, width=40, height=6,
                                   font=StyleManager.FONTS['body'])
        self.problem_text.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        if self.request_data:
            self.problem_text.insert('1.0', self.request_data['problemDescription'])
        
        row += 1
        
        # Клиент
        ttk.Label(fields_frame, text="Клиент:*", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.W, pady=(0, 10))
        
        client_frame = ttk.Frame(fields_frame)
        client_frame.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        # Выбор существующего клиента
        self.client_var = tk.StringVar()
        client_values = [f"{c[0]}: {c[1]} ({c[2]})" for c in self.clients] if self.clients else []
        client_combo = ttk.Combobox(client_frame, textvariable=self.client_var,
                                   values=client_values,
                                   state='normal',
                                   width=30)
        client_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка нового клиента
        if self.mode != 'view':
            ttk.Button(client_frame, text="➕ Новый",
                      style='Info.TButton',
                      command=self.add_new_client).pack(side=tk.LEFT)
        
        if self.request_data and self.request_data.get('client_name'):
            client_combo.set(f"{self.request_data['clientID']}: {self.request_data['client_name']} ({self.request_data['client_phone']})")
        
        row += 1
        
        # Телефон клиента
        ttk.Label(fields_frame, text="Телефон клиента:*", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.W, pady=(0, 10))
        
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(fields_frame, textvariable=self.phone_var,
                               style='Modern.TEntry', width=33)
        phone_entry.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        if self.request_data:
            phone_entry.insert(0, self.request_data['client_phone'])
        
        row += 1
        
        # Мастер
        if self.user.has_permission('assign_master') or self.mode == 'view':
            ttk.Label(fields_frame, text="Мастер:", 
                     style='Body.TLabel').grid(row=row, column=0, 
                                              sticky=tk.W, pady=(0, 10))
            
            self.master_var = tk.StringVar()
            master_values = [f"{m[0]}: {m[1]}" for m in self.masters] if self.masters else []
            master_combo = ttk.Combobox(fields_frame, textvariable=self.master_var,
                                       values=master_values,
                                       state='readonly' if self.mode == 'view' else 'normal',
                                       width=30)
            master_combo.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
            
            if self.request_data and self.request_data.get('master_name'):
                master_combo.set(f"{self.request_data['masterID']}: {self.request_data['master_name']}")
            
            row += 1
        
        # Запчасти
        ttk.Label(fields_frame, text="Использованные запчасти:", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.NW, pady=(0, 10))
        
        self.parts_text = tk.Text(fields_frame, width=40, height=4,
                                 font=StyleManager.FONTS['body'])
        self.parts_text.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        if self.request_data and self.request_data['repairParts']:
            self.parts_text.insert('1.0', self.request_data['repairParts'])
        
        row += 1
        
        # Стоимость
        ttk.Label(fields_frame, text="Ориентировочная стоимость:", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.W, pady=(0, 10))
        
        self.estimated_cost_var = tk.DoubleVar(value=self.request_data.get('estimatedCost', 0) if self.request_data else 0)
        cost_entry = ttk.Entry(fields_frame, textvariable=self.estimated_cost_var,
                              style='Modern.TEntry', width=33)
        cost_entry.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        row += 1
        
        # Дата завершения
        if self.mode != 'create':
            ttk.Label(fields_frame, text="Дата завершения:", 
                     style='Body.TLabel').grid(row=row, column=0, 
                                              sticky=tk.W, pady=(0, 10))
            
            self.completion_date_var = tk.StringVar(value=self.request_data.get('completionDate', '') if self.request_data else '')
            date_entry = ttk.Entry(fields_frame, textvariable=self.completion_date_var,
                                  style='Modern.TEntry', width=33)
            date_entry.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
            
            if self.mode != 'view':
                ttk.Button(fields_frame, text="Сегодня",
                          style='Info.TButton',
                          command=lambda: self.completion_date_var.set(datetime.now().strftime("%Y-%m-%d"))
                          ).grid(row=row, column=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
            
            row += 1
        
        # Примечания
        ttk.Label(fields_frame, text="Примечания:", 
                 style='Body.TLabel').grid(row=row, column=0, 
                                          sticky=tk.NW, pady=(0, 10))
        
        self.notes_text = tk.Text(fields_frame, width=40, height=4,
                                 font=StyleManager.FONTS['body'])
        self.notes_text.grid(row=row, column=1, sticky=tk.W, pady=(0, 10))
        
        if self.request_data and self.request_data['notes']:
            self.notes_text.insert('1.0', self.request_data['notes'])
        
        # Настройка сетки
        fields_frame.columnconfigure(1, weight=1)
    
    def setup_comments_tab(self, notebook):
        """Настройка вкладки комментариев"""
        comments_frame = ttk.Frame(notebook)
        notebook.add(comments_frame, text="💬 Комментарии")
        
        # Форма для нового комментария
        if self.mode != 'view' and self.user.type in ['Мастер', 'Менеджер', 'Оператор', 'Менеджер качества']:
            new_comment_card = Card(comments_frame, title="Новый комментарий")
            new_comment_card.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            self.new_comment_text = tk.Text(new_comment_card.content_frame, 
                                           height=4,
                                           font=StyleManager.FONTS['body'])
            self.new_comment_text.pack(fill=tk.X, padx=10, pady=10)
            
            button_frame = ttk.Frame(new_comment_card.content_frame)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            ttk.Button(button_frame, text="Добавить комментарий",
                      style='Primary.TButton',
                      command=self.add_comment).pack(side=tk.LEFT)
            
            # Checkbox для приватного комментария
            self.private_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(button_frame, text="Приватный",
                           variable=self.private_var,
                           style='Modern.TCheckbutton').pack(side=tk.LEFT, padx=(20, 0))
        
        # Список комментариев
        comments_list_card = Card(comments_frame, title="История комментариев")
        comments_list_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Контейнер с прокруткой
        canvas = tk.Canvas(comments_list_card.content_frame, 
                          bg=StyleManager.COLORS['white'])
        scrollbar = ttk.Scrollbar(comments_list_card.content_frame, 
                                 orient=tk.VERTICAL, 
                                 command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Отображение комментариев
        if hasattr(self, 'comments') and self.comments:
            for comment in self.comments:
                self._create_comment_widget(scrollable_frame, comment)
        else:
            ttk.Label(scrollable_frame, text="Комментариев пока нет",
                     style='Body.TLabel',
                     foreground=StyleManager.COLORS['gray']).pack(pady=20)
    
    def _create_comment_widget(self, parent, comment):
        """Создать виджет комментария"""
        comment_card = Card(parent, padding=10)
        comment_card.pack(fill=tk.X, pady=5, padx=5)
        
        # Заголовок
        header_frame = ttk.Frame(comment_card.content_frame)
        header_frame.pack(fill=tk.X)
        
        # Аватар автора
        avatar = Avatar(header_frame, text=comment['author_name'][:2], size=30)
        avatar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Информация об авторе
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(info_frame, text=comment['author_name'],
                 style='Body.TLabel').pack(anchor=tk.W)
        
        # Время
        time_frame = ttk.Frame(header_frame)
        time_frame.pack(side=tk.RIGHT)
        
        ttk.Label(time_frame, text=comment['timestamp'][:16],
                 style='Small.TLabel',
                 foreground=StyleManager.COLORS['gray']).pack(anchor=tk.E)
        
        # Приватный комментарий
        if comment['is_private']:
            ttk.Label(time_frame, text="🔒 Приватный",
                     style='Small.TLabel',
                     foreground=StyleManager.COLORS['warning']).pack(anchor=tk.E, pady=(0, 2))
        
        # Текст комментария
        text_frame = ttk.Frame(comment_card.content_frame)
        text_frame.pack(fill=tk.X, padx=35, pady=(5, 0))
        
        comment_text = tk.Text(text_frame, height=3, wrap=tk.WORD,
                              bg=StyleManager.COLORS['light'],
                              relief='flat',
                              font=StyleManager.FONTS['body'])
        comment_text.insert('1.0', comment['message'])
        comment_text.configure(state='disabled')
        comment_text.pack(fill=tk.X)
    
    def setup_parts_tab(self, notebook):
        """Настройка вкладки запчастей"""
        parts_frame = ttk.Frame(notebook)
        notebook.add(parts_frame, text="🔧 Запчасти")
        
        # Добавление запчастей
        if self.mode != 'view' and self.user.has_permission('edit_request'):
            add_parts_card = Card(parts_frame, title="Добавить запчасти")
            add_parts_card.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            # Выбор запчасти
            selection_frame = ttk.Frame(add_parts_card.content_frame)
            selection_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(selection_frame, text="Запчасть:", 
                     style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
            
            # Получение списка запчастей
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT partID, partName, price FROM parts ORDER BY partName')
                parts_list = cursor.fetchall()
            
            self.part_var = tk.StringVar()
            part_values = [f"{p[0]}: {p[1]} ({p[2]}₽)" for p in parts_list]
            part_combo = ttk.Combobox(selection_frame, textvariable=self.part_var,
                                     values=part_values,
                                     state='normal',
                                     width=40)
            part_combo.pack(side=tk.LEFT, padx=(0, 10))
            
            # Количество
            ttk.Label(selection_frame, text="Количество:", 
                     style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
            
            self.quantity_var = tk.IntVar(value=1)
            quantity_spin = ttk.Spinbox(selection_frame, from_=1, to=100,
                                       textvariable=self.quantity_var,
                                       width=10)
            quantity_spin.pack(side=tk.LEFT, padx=(0, 10))
            
            # Кнопка добавления
            ttk.Button(selection_frame, text="Добавить",
                      style='Success.TButton',
                      command=self.add_part_to_request).pack(side=tk.LEFT)
        
        # Список использованных запчастей
        parts_list_card = Card(parts_frame, title="Использованные запчасти")
        parts_list_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Таблица запчастей
        columns = ("ID", "Наименование", "Артикул", "Цена", "Количество", "Сумма")
        
        self.parts_tree = ttk.Treeview(parts_list_card.content_frame, 
                                      columns=columns, 
                                      style='Modern.Treeview',
                                      height=10,
                                      show="headings")
        
        for col in columns:
            self.parts_tree.heading(col, text=col)
            self.parts_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(parts_list_card.content_frame,
                                 orient=tk.VERTICAL,
                                 command=self.parts_tree.yview)
        self.parts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.parts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Загрузка данных
        self.load_parts_list()
    
    def setup_feedback_tab(self, notebook):
        """Настройка вкладки обратной связи"""
        feedback_frame = ttk.Frame(notebook)
        notebook.add(feedback_frame, text="⭐ Оценка")
        
        feedback_card = Card(feedback_frame, title="Оценка качества обслуживания")
        feedback_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        content = ttk.Frame(feedback_card.content_frame)
        content.pack(expand=True)
        
        # Генерация QR-кода
        qr_file = QRCodeGenerator.generate_feedback_qr(self.request_id)
        
        try:
            # Загрузка и отображение QR-кода
            img = Image.open(qr_file)
            img = img.resize((250, 250), Image.Resampling.LANCZOS)
            self.qr_photo = ImageTk.PhotoImage(img)
            
            qr_label = ttk.Label(content, image=self.qr_photo)
            qr_label.pack(pady=20)
            
            # Инструкция
            instruction = """
            Отсканируйте QR-код для оценки работы мастера.
            
            Клиент может оценить:
            • Качество ремонта
            • Скорость выполнения
            • Вежливость персонала
            • Общее впечатление
            """
            
            ttk.Label(content, text=instruction,
                     style='Body.TLabel',
                     justify=tk.CENTER).pack(pady=20)
            
            # Кнопка отправки ссылки
            ttk.Button(content, text="📧 Отправить ссылку клиенту",
                      style='Primary.TButton',
                      command=self.send_feedback_link).pack(pady=10)
            
        except Exception as e:
            ttk.Label(content, text=f"Ошибка загрузки QR-кода: {e}",
                     style='Body.TLabel',
                     foreground=StyleManager.COLORS['danger']).pack(pady=20)
    
    def setup_button_panel(self, parent):
        """Панель кнопок действий"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        if self.mode == 'create':
            ttk.Button(button_frame, text="Создать заявку",
                      style='Success.TButton',
                      command=self.create_request).pack(side=tk.RIGHT, padx=5)
        
        elif self.mode == 'edit':
            ttk.Button(button_frame, text="Сохранить изменения",
                      style='Primary.TButton',
                      command=self.update_request).pack(side=tk.RIGHT, padx=5)
            
            # Кнопка клонирования заявки
            ttk.Button(button_frame, text="Клонировать",
                      style='Info.TButton',
                      command=self.clone_request).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Закрыть",
                  command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def set_readonly(self):
        """Установить режим только для чтения"""
        for widget in self.window.winfo_children():
            self._set_widget_readonly(widget)
    
    def _set_widget_readonly(self, widget):
        """Рекурсивно установить режим только для чтения"""
        if isinstance(widget, (ttk.Entry, tk.Text)):
            widget.configure(state='disabled')
        elif isinstance(widget, ttk.Combobox):
            widget.configure(state='disabled')
        elif isinstance(widget, ttk.Spinbox):
            widget.configure(state='disabled')
        elif isinstance(widget, ttk.Button):
            if widget.cget('text') not in ['Закрыть', 'Сегодня']:
                widget.configure(state='disabled')
        
        # Рекурсивно обрабатываем дочерние виджеты
        for child in widget.winfo_children():
            self._set_widget_readonly(child)
    
    def add_new_client(self):
        """Добавить нового клиента"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Новый клиент")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="ФИО клиента:*", 
                 style='Body.TLabel').pack(pady=(20, 5))
        
        fio_var = tk.StringVar()
        fio_entry = ttk.Entry(dialog, textvariable=fio_var,
                             style='Modern.TEntry', width=40)
        fio_entry.pack(pady=(0, 10))
        
        ttk.Label(dialog, text="Телефон:*", 
                 style='Body.TLabel').pack(pady=(0, 5))
        
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(dialog, textvariable=phone_var,
                               style='Modern.TEntry', width=40)
        phone_entry.pack(pady=(0, 20))
        
        def save_client():
            if not fio_var.get() or not phone_var.get():
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            if not Validators.validate_phone(phone_var.get()):
                messagebox.showerror("Ошибка", "Неверный формат телефона")
                return
            
            # Сохранение клиента
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Генерация логина
                import random
                login = f"client_{random.randint(1000, 9999)}"
                
                cursor.execute('''
                    INSERT INTO users (fio, phone, login, password, type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (fio_var.get(), phone_var.get(), login, 'temp_password', 'Заказчик'))
                
                client_id = cursor.lastrowid
                conn.commit()
            
            # Обновление списка клиентов
            self.clients.append((client_id, fio_var.get(), phone_var.get()))
            
            # Обновление combobox
            self.client_var.set(f"{client_id}: {fio_var.get()} ({phone_var.get()})")
            self.phone_var.set(phone_var.get())
            
            dialog.destroy()
            messagebox.showinfo("Успех", "Клиент добавлен")
        
        ttk.Button(dialog, text="Сохранить",
                  style='Primary.TButton',
                  command=save_client).pack(pady=20)
    
    def add_comment(self):
        """Добавить комментарий"""
        comment_text = self.new_comment_text.get("1.0", tk.END).strip()
        
        if not comment_text:
            messagebox.showwarning("Внимание", "Введите текст комментария")
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO comments (message, masterID, requestID, is_private)
                VALUES (?, ?, ?, ?)
            ''', (comment_text, self.user.userID, self.request_id, 
                  int(self.private_var.get())))
            conn.commit()
        
        self.new_comment_text.delete("1.0", tk.END)
        
        # Обновление списка комментариев
        self.load_data()
        
        # Перезагрузка вкладки комментариев
        notebook = self.window.winfo_children()[0].winfo_children()[0]
        notebook.tab(1, state='normal')  # Вторая вкладка
        
        messagebox.showinfo("Успех", "Комментарий добавлен")
    
    def add_part_to_request(self):
        """Добавить запчасть к заявке"""
        part_text = self.part_var.get()
        if not part_text:
            messagebox.showwarning("Внимание", "Выберите запчасть")
            return
        
        try:
            part_id = int(part_text.split(":")[0])
            quantity = self.quantity_var.get()
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Проверяем, есть ли уже эта запчасть в заявке
                cursor.execute('''
                    SELECT quantity FROM request_parts 
                    WHERE requestID = ? AND partID = ?
                ''', (self.request_id, part_id))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Обновляем количество
                    new_quantity = existing[0] + quantity
                    cursor.execute('''
                        UPDATE request_parts 
                        SET quantity = ?
                        WHERE requestID = ? AND partID = ?
                    ''', (new_quantity, self.request_id, part_id))
                else:
                    # Добавляем новую запчасть
                    cursor.execute('''
                        INSERT INTO request_parts (requestID, partID, quantity)
                        VALUES (?, ?, ?)
                    ''', (self.request_id, part_id, quantity))
                
                conn.commit()
            
            # Обновление списка
            self.load_parts_list()
            
            # Очистка полей
            self.part_var.set('')
            self.quantity_var.set(1)
            
            messagebox.showinfo("Успех", "Запчасть добавлена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запчасть: {e}")
    
    def load_parts_list(self):
        """Загрузка списка запчастей"""
        if not hasattr(self, 'parts_tree'):
            return
        
        # Очищаем таблицу
        for item in self.parts_tree.get_children():
            self.parts_tree.delete(item)
        
        if not self.request_id:
            return
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.partID, p.partName, p.vendorCode, p.price, rp.quantity
                FROM parts p
                JOIN request_parts rp ON p.partID = rp.partID
                WHERE rp.requestID = ?
            ''', (self.request_id,))
            
            total_cost = 0
            
            for row in cursor.fetchall():
                part_id, name, vendor, price, quantity = row
                total = price * quantity
                total_cost += total
                
                self.parts_tree.insert('', tk.END, values=(
                    part_id, name, vendor, f"{price:.2f}₽", quantity, f"{total:.2f}₽"
                ))
            
            # Итоговая строка
            if total_cost > 0:
                self.parts_tree.insert('', tk.END, values=(
                    "", "ИТОГО:", "", "", "", f"{total_cost:.2f}₽"
                ))
    
    def send_feedback_link(self):
        """Отправить ссылку для оценки"""
        feedback_url = f"https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?entry.123456789={self.request_id}"
        
        # В реальном приложении здесь была бы отправка email/SMS
        messagebox.showinfo("Ссылка для оценки", 
                          f"Ссылка для оценки качества:\n\n{feedback_url}\n\n"
                          "Ссылка скопирована в буфер обмена.")
        
        # Копирование в буфер обмена
        self.window.clipboard_clear()
        self.window.clipboard_append(feedback_url)
    
    def clone_request(self):
        """Клонировать заявку"""
        if not self.request_data:
            return
        
        response = messagebox.askyesno("Клонирование", 
                                      "Создать копию этой заявки?")
        
        if response:
            # Открываем новую форму с данными текущей заявки
            RequestForm(self.parent, self.user, self.db, self.callback, 
                       mode='create')
            
            # Здесь можно предзаполнить поля данными из текущей заявки
            # В реальном приложении нужно передать данные
    
    def create_request(self):
        """Создать новую заявку"""
        if not self._validate_input():
            return
        
        # Получаем ID клиента
        client_text = self.client_var.get()
        if not client_text:
            messagebox.showerror("Ошибка", "Выберите клиента")
            return
        
        try:
            client_id = int(client_text.split(":")[0])
        except:
            messagebox.showerror("Ошибка", "Неверный формат клиента")
            return
        
        # Получаем ID мастера (если выбран)
        master_id = None
        if hasattr(self, 'master_var') and self.master_var.get():
            try:
                master_id = int(self.master_var.get().split(":")[0])
            except:
                pass
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Создаем заявку
            cursor.execute('''
                INSERT INTO requests 
                (startDate, homeTechType, homeTechModel, problemDescription, 
                 requestStatus, masterID, clientID, priority, estimatedCost, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime("%Y-%m-%d"),
                self.tech_type_var.get(),
                self.model_var.get(),
                self.problem_text.get("1.0", tk.END).strip(),
                "Новая заявка",
                master_id,
                client_id,
                self.priority_var.get(),
                self.estimated_cost_var.get(),
                self.notes_text.get("1.0", tk.END).strip()
            ))
            
            request_id = cursor.lastrowid
            conn.commit()
        
        # Добавление уведомления
        self.db.add_notification(master_id if master_id else 1,  # Администратору
                                f"Создана новая заявка #{request_id}",
                                'info')
        
        messagebox.showinfo("Успех", f"Заявка #{request_id} успешно создана")
        self.window.destroy()
        self.callback()
    
    def update_request(self):
        """Обновить заявку"""
        if not self._validate_input():
            return
        
        # Получаем ID мастера (если выбран)
        master_id = None
        if hasattr(self, 'master_var') and self.master_var.get():
            try:
                master_id = int(self.master_var.get().split(":")[0])
            except:
                pass
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Обновляем заявку
            cursor.execute('''
                UPDATE requests 
                SET homeTechType = ?,
                    homeTechModel = ?,
                    problemDescription = ?,
                    requestStatus = ?,
                    repairParts = ?,
                    completionDate = ?,
                    masterID = ?,
                    priority = ?,
                    estimatedCost = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE requestID = ?
            ''', (
                self.tech_type_var.get(),
                self.model_var.get(),
                self.problem_text.get("1.0", tk.END).strip(),
                self.status_var.get(),
                self.parts_text.get("1.0", tk.END).strip(),
                self.completion_date_var.get() if hasattr(self, 'completion_date_var') else None,
                master_id,
                self.priority_var.get(),
                self.estimated_cost_var.get(),
                self.notes_text.get("1.0", tk.END).strip(),
                self.request_id
            ))
            
            conn.commit()
        
        messagebox.showinfo("Успех", "Изменения сохранены")
        self.window.destroy()
        self.callback()
    
    def _validate_input(self):
        """Валидация введенных данных"""
        # Проверка обязательных полей
        if not self.tech_type_var.get():
            messagebox.showerror("Ошибка", "Укажите тип техники")
            return False
        
        if not self.model_var.get():
            messagebox.showerror("Ошибка", "Укажите модель техники")
            return False
        
        if not self.problem_text.get("1.0", tk.END).strip():
            messagebox.showerror("Ошибка", "Опишите проблему")
            return False
        
        if not self.client_var.get():
            messagebox.showerror("Ошибка", "Выберите клиента")
            return False
        
        if not self.phone_var.get():
            messagebox.showerror("Ошибка", "Укажите телефон клиента")
            return False
        
        # Валидация телефона
        if not Validators.validate_phone(self.phone_var.get()):
            messagebox.showerror("Ошибка", "Неверный формат телефона")
            return False
        
        # Валидация стоимости
        try:
            cost = float(self.estimated_cost_var.get())
            if cost < 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Неверная стоимость")
            return False
        
        return True