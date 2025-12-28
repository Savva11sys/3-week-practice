import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from styles import StyleManager
from widgets import Card, MetricCard, StatusBadge, SearchBox

class QualityManagerForm(ttk.Frame):
    """Форма менеджера по качеству"""
    
    def __init__(self, parent, user, db):
        super().__init__(parent)
        self.user = user
        self.db = db
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Контейнер с прокруткой
        canvas = tk.Canvas(self, bg=StyleManager.COLORS['light'])
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, 
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
        
        # Метрики
        metrics_frame = ttk.Frame(scrollable_frame)
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.overdue_metric = MetricCard(metrics_frame, "Просрочено", "0",
                                        icon="⚠️", color=StyleManager.COLORS['danger'])
        self.overdue_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.extended_metric = MetricCard(metrics_frame, "Продлено", "0",
                                         icon="📅", color=StyleManager.COLORS['warning'])
        self.extended_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.complaints_metric = MetricCard(metrics_frame, "Жалобы", "0",
                                           icon="😠", color=StyleManager.COLORS['danger'])
        self.complaints_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.satisfaction_metric = MetricCard(metrics_frame, "Удовлетворенность", "0", "%",
                                             icon="⭐", color=StyleManager.COLORS['success'])
        self.satisfaction_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Панель поиска
        search_card = Card(scrollable_frame, title="Поиск просроченных заявок")
        search_card.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        search_frame = ttk.Frame(search_card.content_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Порог просрочки:", 
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.threshold_var = tk.IntVar(value=7)
        threshold_spin = ttk.Spinbox(search_frame, from_=1, to=30,
                                    textvariable=self.threshold_var,
                                    width=5)
        threshold_spin.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(search_frame, text="Обновить",
                  style='Primary.TButton',
                  command=self.refresh).pack(side=tk.LEFT)
        
        # Таблица просроченных заявок
        table_card = Card(scrollable_frame, title="Просроченные заявки")
        table_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Таблица
        columns = ("ID", "Дата", "Техника", "Статус", "Клиент", "Мастер", "Дней", "Действия")
        
        self.overdue_tree = ttk.Treeview(table_card.content_frame, columns=columns, 
                                        style='Modern.Treeview',
                                        show="headings",
                                        height=15)
        
        col_widths = [50, 80, 100, 100, 120, 100, 60, 150]
        for idx, col in enumerate(columns):
            self.overdue_tree.heading(col, text=col)
            self.overdue_tree.column(col, width=col_widths[idx])
        
        scrollbar = ttk.Scrollbar(table_card.content_frame,
                                 orient=tk.VERTICAL,
                                 command=self.overdue_tree.yview)
        self.overdue_tree.configure(yscrollcommand=scrollbar.set)
        
        self.overdue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Контекстное меню
        self.setup_context_menu()
        
        # Статистика качества
        stats_card = Card(scrollable_frame, title="Статистика качества")
        stats_card.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        stats_frame = ttk.Frame(stats_card.content_frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Здесь можно добавить графики или таблицы со статистикой
    
    def setup_context_menu(self):
        """Контекстное меню для таблицы"""
        self.context_menu = tk.Menu(self.overdue_tree, tearoff=0)
        
        self.context_menu.add_command(label="📅 Продлить срок", 
                                     command=self.extend_deadline)
        self.context_menu.add_command(label="🔧 Назначить мастера", 
                                     command=self.assign_master)
        self.context_menu.add_command(label="📞 Связаться с клиентом", 
                                     command=self.contact_client)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📝 Добавить примечание", 
                                     command=self.add_note)
        
        self.overdue_tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.overdue_tree.identify_row(event.y)
        if item:
            self.overdue_tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def refresh(self):
        """Обновление данных"""
        try:
            # Получение просроченных заявок
            threshold = self.threshold_var.get()
            overdue_requests = self.db.get_overdue_requests(threshold)
            
            # Обновление метрик
            self.overdue_metric.update_value(len(overdue_requests))
            
            # Подсчет продленных заявок
            extended_count = sum(1 for r in overdue_requests if r.get('extendedDeadline'))
            self.extended_metric.update_value(extended_count)
            
            # Очистка таблицы
            for item in self.overdue_tree.get_children():
                self.overdue_tree.delete(item)
            
            # Заполнение таблицы
            for req in overdue_requests:
                days_passed = int(req.get('days_passed', 0))
                
                # Кнопки действий
                actions_frame = ttk.Frame(self.overdue_tree)
                
                ttk.Button(actions_frame, text="Продлить",
                          style='Warning.TButton',
                          command=lambda r=req: self.extend_deadline_dialog(r)).pack(side=tk.LEFT, padx=2)
                
                ttk.Button(actions_frame, text="Мастер",
                          style='Info.TButton',
                          command=lambda r=req: self.assign_master_dialog(r)).pack(side=tk.LEFT, padx=2)
                
                values = (
                    req['requestID'],
                    req['startDate'],
                    req['homeTechType'],
                    req['requestStatus'],
                    req.get('client_name', ''),
                    req.get('master_name', ''),
                    days_passed,
                    ""  # Действия будут отображаться отдельно
                )
                
                item = self.overdue_tree.insert('', tk.END, values=values)
                
                # Подсветка сильно просроченных
                if days_passed > 14:
                    self.overdue_tree.item(item, tags=('critical',))
                elif days_passed > 7:
                    self.overdue_tree.item(item, tags=('warning',))
            
            # Настройка тегов
            self.overdue_tree.tag_configure('warning', background=StyleManager.COLORS['warning_light'])
            self.overdue_tree.tag_configure('critical', background=StyleManager.COLORS['danger_light'])
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
    
    def extend_deadline_dialog(self, request):
        """Диалог продления срока"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Продление срока заявки #{request['requestID']}")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text=f"Заявка #{request['requestID']}", 
                 style='Heading.TLabel').pack(pady=20)
        
        ttk.Label(dialog, text=f"Клиент: {request.get('client_name', '')}",
                 style='Body.TLabel').pack()
        
        ttk.Label(dialog, text=f"Просрочено на: {int(request.get('days_passed', 0))} дней",
                 style='Body.TLabel').pack(pady=10)
        
        ttk.Label(dialog, text="Дополнительных дней:", 
                 style='Body.TLabel').pack(pady=(20, 5))
        
        days_var = tk.IntVar(value=7)
        days_spin = ttk.Spinbox(dialog, from_=1, to=30,
                               textvariable=days_var,
                               width=10)
        days_spin.pack(pady=(0, 10))
        
        ttk.Label(dialog, text="Причина продления:", 
                 style='Body.TLabel').pack(pady=(10, 5))
        
        reason_text = tk.Text(dialog, height=4, width=40)
        reason_text.pack(pady=(0, 20))
        
        def confirm_extension():
            reason = reason_text.get("1.0", tk.END).strip()
            if not reason:
                messagebox.showwarning("Внимание", "Укажите причину продления")
                return
            
            # Расчет новой даты
            current_date = datetime.strptime(request['startDate'], "%Y-%m-%d")
            new_deadline = (current_date + timedelta(days=days_var.get() + int(request.get('days_passed', 0)))).strftime("%Y-%m-%d")
            
            # Обновление в БД
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE requests 
                    SET extendedDeadline = ?,
                        qualityManagerID = ?,
                        notes = COALESCE(notes || '\n', '') || ?
                    WHERE requestID = ?
                ''', (new_deadline, self.user.userID, 
                     f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Продлено на {days_var.get()} дней. Причина: {reason}",
                     request['requestID']))
                
                conn.commit()
            
            # Уведомление
            self.db.add_notification(request.get('masterID') or 1,
                                   f"Срок заявки #{request['requestID']} продлен на {days_var.get()} дней",
                                   'warning')
            
            dialog.destroy()
            self.refresh()
            messagebox.showinfo("Успех", "Срок продлен")
        
        ttk.Button(dialog, text="Подтвердить",
                  style='Primary.TButton',
                  command=confirm_extension).pack(pady=10)
    
    def assign_master_dialog(self, request):
        """Диалог назначения мастера"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Назначение мастера заявке #{request['requestID']}")
        dialog.geometry("400x250")
        
        ttk.Label(dialog, text="Выберите мастера:", 
                 style='Body.TLabel').pack(pady=20)
        
        # Получение списка мастеров
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT userID, fio FROM users 
                WHERE type = 'Мастер' AND is_active = 1
                ORDER BY fio
            ''')
            masters = cursor.fetchall()
        
        master_var = tk.StringVar()
        master_values = [f"{m[0]}: {m[1]}" for m in masters]
        master_combo = ttk.Combobox(dialog, textvariable=master_var,
                                   values=master_values,
                                   state='readonly',
                                   width=30)
        master_combo.pack(pady=10)
        
        ttk.Label(dialog, text="Причина назначения:", 
                 style='Body.TLabel').pack(pady=(10, 5))
        
        reason_text = tk.Text(dialog, height=3, width=40)
        reason_text.pack(pady=(0, 20))
        
        def confirm_assignment():
            if not master_var.get():
                messagebox.showwarning("Внимание", "Выберите мастера")
                return
            
            master_id = int(master_var.get().split(":")[0])
            reason = reason_text.get("1.0", tk.END).strip()
            
            # Обновление в БД
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE requests 
                    SET masterID = ?,
                        qualityManagerID = ?,
                        notes = COALESCE(notes || '\n', '') || ?
                    WHERE requestID = ?
                ''', (master_id, self.user.userID,
                     f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Назначен новый мастер. Причина: {reason}",
                     request['requestID']))
                
                conn.commit()
            
            # Уведомление мастеру
            self.db.add_notification(master_id,
                                   f"Вам назначена заявка #{request['requestID']}",
                                   'info')
            
            dialog.destroy()
            self.refresh()
            messagebox.showinfo("Успех", "Мастер назначен")
        
        ttk.Button(dialog, text="Назначить",
                  style='Primary.TButton',
                  command=confirm_assignment).pack(pady=10)
    
    def extend_deadline(self):
        """Продлить срок выбранной заявки"""
        selection = self.overdue_tree.selection()
        if selection:
            item = self.overdue_tree.item(selection[0])
            request_id = item['values'][0]
            
            # Поиск данных заявки
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.*, c.fio as client_name
                    FROM requests r
                    LEFT JOIN users c ON r.clientID = c.userID
                    WHERE r.requestID = ?
                ''', (request_id,))
                
                request = dict(cursor.fetchone())
            
            if request:
                self.extend_deadline_dialog(request)
    
    def assign_master(self):
        """Назначить мастера выбранной заявке"""
        selection = self.overdue_tree.selection()
        if selection:
            item = self.overdue_tree.item(selection[0])
            request_id = item['values'][0]
            
            # Поиск данных заявки
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.*, c.fio as client_name
                    FROM requests r
                    LEFT JOIN users c ON r.clientID = c.userID
                    WHERE r.requestID = ?
                ''', (request_id,))
                
                request = dict(cursor.fetchone())
            
            if request:
                self.assign_master_dialog(request)
    
    def contact_client(self):
        """Связаться с клиентом"""
        selection = self.overdue_tree.selection()
        if selection:
            item = self.overdue_tree.item(selection[0])
            request_id = item['values'][0]
            client_name = item['values'][4]
            
            # Получение телефона клиента
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.phone FROM users u
                    JOIN requests r ON u.userID = r.clientID
                    WHERE r.requestID = ?
                ''', (request_id,))
                
                result = cursor.fetchone()
                if result:
                    phone = result[0]
                    
                    # В реальном приложении здесь была бы интеграция с телефонией
                    messagebox.showinfo("Контакт клиента", 
                                      f"Клиент: {client_name}\n"
                                      f"Телефон: {phone}\n\n"
                                      f"Заявка: #{request_id}")
    
    def add_note(self):
        """Добавить примечание к заявке"""
        selection = self.overdue_tree.selection()
        if not selection:
            return
        
        item = self.overdue_tree.item(selection[0])
        request_id = item['values'][0]
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Примечание к заявке #{request_id}")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="Текст примечания:", 
                 style='Body.TLabel').pack(pady=20)
        
        note_text = tk.Text(dialog, height=8, width=50)
        note_text.pack(pady=(0, 20), padx=20)
        
        def save_note():
            note = note_text.get("1.0", tk.END).strip()
            if not note:
                messagebox.showwarning("Внимание", "Введите текст примечания")
                return
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE requests 
                    SET notes = COALESCE(notes || '\n', '') || ?,
                        qualityManagerID = ?
                    WHERE requestID = ?
                ''', (f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note}",
                     self.user.userID, request_id))
                
                conn.commit()
            
            dialog.destroy()
            messagebox.showinfo("Успех", "Примечание добавлено")
        
        ttk.Button(dialog, text="Сохранить",
                  style='Primary.TButton',
                  command=save_note).pack(pady=10)