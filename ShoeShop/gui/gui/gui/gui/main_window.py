import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        
        # Названия ролей
        role_names = {
            'guest': 'Гость',
            'client': 'Клиент',
            'manager': 'Менеджер',
            'admin': 'Администратор'
        }
        role_display = role_names.get(user['role'], user['role'])
        
        self.root.title(f"Магазин обуви - {role_display}")
        self.root.geometry("1000x700")
        
        # Центрируем окно
        self.center_window()
        
        # Верхняя панель
        self.setup_header()
        
        # Основное меню
        self.setup_menu()
        
        # Основная область с вкладками
        self.setup_main_area()
        
        # Показываем товары по умолчанию
        self.show_products()
    
    def center_window(self):
        """Центрирование окна"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
    def setup_header(self):
        """Верхняя панель с информацией о пользователе"""
        header = tk.Frame(self.root, bg="#34495e", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Логотип (текстовый)
        logo = tk.Label(
            header,
            text="👞 ShoeShop",
            bg="#34495e",
            fg="white",
            font=("Arial", 16, "bold")
        )
        logo.pack(side="left", padx=20)
        
        # Информация о пользователе
        user_frame = tk.Frame(header, bg="#34495e")
        user_frame.pack(side="right", padx=20)
        
        # Иконка пользователя
        user_icon = tk.Label(
            user_frame,
            text="👤",
            bg="#34495e",
            fg="white",
            font=("Arial", 14)
        )
        user_icon.pack(side="left", padx=5)
        
        # ФИО пользователя
        user_name = tk.Label(
            user_frame,
            text=self.user['full_name'],
            bg="#34495e",
            fg="white",
            font=("Arial", 11)
        )
        user_name.pack(side="left", padx=5)
        
        # Кнопка выхода
        logout_btn = tk.Button(
            header,
            text="🚪 Выйти",
            command=self.logout,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            bd=0,
            padx=10
        )
        logout_btn.pack(side="right", padx=10)
    
    def setup_menu(self):
        """Создание меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.logout)
        
        # Меню Товары (для всех)
        products_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Товары", menu=products_menu)
        products_menu.add_command(label="Список товаров", command=self.show_products)
        
        # Для админа - добавление товара
        if self.user['role'] == 'admin':
            products_menu.add_separator()
            products_menu.add_command(label="➕ Добавить товар", command=self.add_product)
        
        # Меню Заказы (для менеджера и админа)
        if self.user['role'] in ['manager', 'admin']:
            orders_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Заказы", menu=orders_menu)
            orders_menu.add_command(label="Все заказы", command=self.show_orders)
    
    def setup_main_area(self):
        """Основная область с вкладками"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_products(self):
        """Показать список товаров"""
        # Очищаем вкладки
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Создаем вкладку с товарами
        from gui.product_list import ProductListWindow
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="📦 Товары")
        ProductListWindow(products_frame, self.user, self)
    
    def add_product(self):
        """Добавление товара (только админ)"""
        from gui.product_edit import ProductEditWindow
        ProductEditWindow(self.root, self.user, product_id=None, parent_window=self)
    
    def show_orders(self):
        """Показать заказы"""
        # Проверяем, есть ли уже вкладка с заказами
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == "📋 Заказы":
                self.notebook.select(tab)
                return
        
        # Создаем новую вкладку
        from gui.orders_window import OrdersWindow
        orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(orders_frame, text="📋 Заказы")
        OrdersWindow(orders_frame, self.user, self)
        self.notebook.select(orders_frame)
    
    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите выйти?"):
            self.root.destroy()
            from gui.login_window import LoginWindow
            LoginWindow().run()
    
    def refresh_products(self):
        """Обновление списка товаров"""
        # Находим вкладку с товарами и обновляем её
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == "📦 Товары":
                # Получаем содержимое вкладки и вызываем refresh
                content = self.nametowidget(tab)
                for child in content.winfo_children():
                    if hasattr(child, 'refresh'):
                        child.refresh()
                break