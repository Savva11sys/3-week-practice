import tkinter as tk
from tkinter import messagebox
from styles import StyleManager
from forms.login_form import LoginForm
from forms.main_form import MainForm
from database import Database
from auth import AuthSystem
import os
import sys

class RepairServiceApp:
    """Главный класс приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Инициализация систем
        self.auth = AuthSystem()
        self.db = Database()
        
        # Запуск формы авторизации
        self.show_login()
        
        # Настройка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title("Сервисный центр - Учет заявок")
        self.root.geometry("1200x700")
        
        # Центрирование окна
        self.center_window()
        
        # Иконка приложения
        try:
            self.root.iconbitmap('assets/icons/app_icon.ico')
        except:
            pass
        
        # Применение стилей
        StyleManager.configure_styles()
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_login(self):
        """Показать форму авторизации"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        LoginForm(self.root, self.on_login_success, self.auth)
    
    def on_login_success(self, user):
        """Обработка успешной авторизации"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Показать главную форму
        self.main_form = MainForm(self.root, user, self.db)
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            if hasattr(self, 'db'):
                self.db.get_connection().close()
            self.root.destroy()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

def main():
    """Точка входа в приложение"""
    # Создание необходимых директорий
    directories = ['data/import', 'data/export', 'data/backups', 
                   'assets/icons', 'logs', 'reports']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Запуск приложения
    app = RepairServiceApp()
    app.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")