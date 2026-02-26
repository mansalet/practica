import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Добавляем путь к корневой папке
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db_models import Database

class LoginWindow:
    """Окно авторизации"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Авторизация - Магазин обуви")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        
        # Подключение к БД
        self.db = Database()
        
        # Центрируем окно
        self.center_window()
        
        # Создаем интерфейс
        self.setup_ui()
        
    def center_window(self):
        """Центрирование окна"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'450x400+{x}+{y}')
    
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="👞 Магазин обуви", 
            font=("Arial", 24, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=30)
        
        # Рамка для входа
        login_frame = ttk.LabelFrame(self.root, text="Вход в систему", padding=30)
        login_frame.pack(padx=40, pady=10, fill="both", expand=True)
        
        # Логин
        tk.Label(login_frame, text="Логин:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", pady=(10, 5)
        )
        self.login_entry = ttk.Entry(login_frame, width=30, font=("Arial", 10))
        self.login_entry.grid(row=0, column=1, pady=(10, 5), padx=10)
        self.login_entry.focus()
        
        # Пароль
        tk.Label(login_frame, text="Пароль:", font=("Arial", 11)).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.password_entry = ttk.Entry(login_frame, width=30, font=("Arial", 10), show="•")
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Привязываем Enter
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Кнопки
        button_frame = tk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=30)
        
        self.login_btn = tk.Button(
            button_frame, 
            text="🔑 Войти", 
            command=self.login,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=1,
            cursor="hand2"
        )
        self.login_btn.pack(side="left", padx=5)
        
        self.guest_btn = tk.Button(
            button_frame, 
            text="👤 Войти как гость", 
            command=self.guest_login,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            width=15,
            height=1,
            cursor="hand2"
        )
        self.guest_btn.pack(side="left", padx=5)
        
        # Подсказка
        hint_frame = tk.Frame(self.root, bg="#ecf0f1")
        hint_frame.pack(fill="x", padx=20, pady=20)
        
        hint_text = """📝 Тестовые учетные записи:
• admin / 123 (Администратор)
• manager / 123 (Менеджер)
• client / 123 (Клиент)
• guest (кнопка "Войти как гость")"""
        
        tk.Label(
            hint_frame, 
            text=hint_text,
            font=("Arial", 9),
            justify="left",
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=10)
    
    def login(self):
        """Обработка входа"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get()
        
        if not login:
            messagebox.showerror(
                "Ошибка входа",
                "Пожалуйста, введите логин"
            )
            return
        
        # Блокируем кнопки на время проверки
        self.login_btn.config(state="disabled")
        self.guest_btn.config(state="disabled")
        
        try:
            user = self.db.check_user(login, password)
            
            if user:
                self.root.destroy()
                # Импортируем здесь, чтобы избежать циклического импорта
                from gui.main_window import MainWindow
                MainWindow(user)
            else:
                messagebox.showerror(
                    "Ошибка входа",
                    "Неверный логин или пароль"
                )
                self.password_entry.delete(0, tk.END)
        finally:
            # Разблокируем кнопки
            self.login_btn.config(state="normal")
            self.guest_btn.config(state="normal")
    
    def guest_login(self):
        """Вход как гость"""
        self.root.destroy()
        from gui.main_window import MainWindow
        guest_user = {
            'id': 0,
            'full_name': 'Гость',
            'role': 'guest'
        }
        MainWindow(guest_user)
    
    def run(self):
        """Запуск окна"""
        self.root.mainloop()