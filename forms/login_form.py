import tkinter as tk
from tkinter import ttk, messagebox
from styles import StyleManager
from widgets import Card, Avatar, LoadingSpinner

class LoginForm:
    """Современная форма авторизации"""
    
    def __init__(self, master, on_login_success, auth_system):
        self.master = master
        self.on_login_success = on_login_success
        self.auth = auth_system
        
        self.setup_ui()
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
        self.master.title("Вход в систему - Сервисный центр")
        self.master.geometry("500x650")
        self.master.resizable(False, False)
        
        # Фоновый градиент
        bg_frame = tk.Frame(self.master)
        bg_frame.place(relwidth=1, relheight=1)
        
        gradient_canvas = StyleManager.create_gradient_canvas(
            bg_frame,
            [StyleManager.hex_to_rgb(StyleManager.COLORS['primary']),
             StyleManager.hex_to_rgb(StyleManager.COLORS['secondary'])],
            500, 650, 'vertical'
        )
        gradient_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Основной контейнер
        main_container = ttk.Frame(self.master)
        main_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Аватар/логотип
        avatar_frame = ttk.Frame(main_container)
        avatar_frame.pack(pady=(0, 20))
        
        avatar = Avatar(avatar_frame, text="SC", size=80, 
                       color=StyleManager.COLORS['white'])
        avatar.pack()
        
        ttk.Label(avatar_frame, text="Сервисный центр",
                 style='Title.TLabel',
                 foreground=StyleManager.COLORS['white']).pack()
        
        ttk.Label(avatar_frame, text="Учет заявок на ремонт",
                 style='Body.TLabel',
                 foreground=StyleManager.COLORS['light']).pack()
        
        # Карточка входа
        login_card = Card(main_container, title="🔐 Вход в систему", 
                         padding=20, rounded=False)
        login_card.pack(padx=20, pady=10)
        
        # Поля формы
        form_frame = ttk.Frame(login_card.content_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле логина
        ttk.Label(form_frame, text="Логин", 
                 style='Subheading.TLabel').grid(row=0, column=0, 
                                                sticky=tk.W, pady=(0, 5))
        
        self.login_entry = ttk.Entry(form_frame, style='Modern.TEntry')
        self.login_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 15))
        
        # Поле пароля
        ttk.Label(form_frame, text="Пароль", 
                 style='Subheading.TLabel').grid(row=2, column=0, 
                                                sticky=tk.W, pady=(0, 5))
        
        password_frame = ttk.Frame(form_frame)
        password_frame.grid(row=3, column=0, sticky=tk.EW, pady=(0, 20))
        
        self.password_entry = ttk.Entry(password_frame, show="●", 
                                       style='Modern.TEntry')
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Кнопка показа пароля
        self.show_pass_var = tk.BooleanVar(value=False)
        show_pass_btn = ttk.Checkbutton(password_frame, text="👁",
                                       variable=self.show_pass_var,
                                       command=self.toggle_password,
                                       style='Modern.TCheckbutton')
        show_pass_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Checkbox "Запомнить меня"
        self.remember_var = tk.BooleanVar(value=False)
        remember_check = ttk.Checkbutton(form_frame, text="Запомнить меня",
                                        variable=self.remember_var,
                                        style='Modern.TCheckbutton')
        remember_check.grid(row=4, column=0, sticky=tk.W, pady=(0, 20))
        
        # Кнопка входа
        self.login_btn = ttk.Button(form_frame, text="Войти", 
                                   style='Primary.TButton',
                                   command=self.login)
        self.login_btn.grid(row=5, column=0, sticky=tk.EW, pady=(10, 5))
        
        # Ссылка "Забыли пароль?"
        forgot_link = ttk.Button(form_frame, text="Забыли пароль?", 
                                style='Flat.TButton',
                                command=self.forgot_password)
        forgot_link.grid(row=6, column=0, pady=(0, 20))
        
        # Настройка сетки
        form_frame.columnconfigure(0, weight=1)
        
        # Демо-доступы
        demo_frame = ttk.Frame(main_container)
        demo_frame.pack(pady=10)
        
        ttk.Label(demo_frame, text="Демо-доступы:", 
                 style='Small.TLabel',
                 foreground=StyleManager.COLORS['light']).pack()
        
        demos = [
            "👑 Менеджер: kasoo / root",
            "🔧 Мастер: murashov123 / qwerty",
            "📞 Оператор: perinaAD / 250519",
            "👤 Заказчик: client1 / pass1",
            "⭐ Менеджер качества: quality / quality123"
        ]
        
        for demo in demos:
            ttk.Label(demo_frame, text=demo,
                     style='Small.TLabel',
                     foreground=StyleManager.COLORS['gray_light']).pack(anchor=tk.W, pady=1)
        
        # Бинды
        self.master.bind('<Return>', lambda e: self.login())
        self.login_entry.focus()
        
        # Спиннер загрузки
        self.loading_spinner = LoadingSpinner(main_container, size=30, 
                                             color=StyleManager.COLORS['white'])
        self.loading_spinner.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        self.loading_spinner.place_forget()
    
    def toggle_password(self):
        """Показать/скрыть пароль"""
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="●")
    
    def login(self, event=None):
        """Выполнить вход"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showwarning("Внимание", "Заполните все поля")
            return
        
        # Показываем спиннер
        self.loading_spinner.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        self.loading_spinner.start()
        self.login_btn.configure(state=tk.DISABLED)
        
        # Имитация задержки (в реальном приложении убрать)
        self.master.after(500, lambda: self._perform_login(login, password))
    
    def _perform_login(self, login, password):
        """Выполнить фактический вход"""
        try:
            if self.auth.login(login, password):
                self.on_login_success(self.auth.current_user)
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
        finally:
            # Скрываем спиннер
            self.loading_spinner.stop()
            self.loading_spinner.place_forget()
            self.login_btn.configure(state=tk.NORMAL)
    
    def forgot_password(self):
        """Обработка забытого пароля"""
        messagebox.showinfo("Восстановление пароля", 
                          "Обратитесь к администратору для восстановления пароля.")
    
    def show_loading(self, show=True):
        """Показать/скрыть индикатор загрузки"""
        if show:
            self.loading_spinner.start()
            self.loading_spinner.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        else:
            self.loading_spinner.stop()
            self.loading_spinner.place_forget()