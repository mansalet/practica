import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db_models import Database

class ProductListWindow:
    """Окно списка товаров"""
    
    def __init__(self, parent, user, main_window):
        self.parent = parent
        self.user = user
        self.main_window = main_window
        self.db = Database()
        
        # Переменные для фильтрации
        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="name_asc")
        self.filter_supplier_var = tk.StringVar(value="all")
        
        # Отслеживаем изменения
        self.search_var.trace('w', lambda *args: self.after_idle(self.apply_filters))
        
        # Для оптимизации производительности
        self.search_after_id = None
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Загружаем товары
        self.load_products()
    
    def after_idle(self, func):
        """Задержка для оптимизации поиска"""
        if self.search_after_id:
            self.parent.after_cancel(self.search_after_id)
        self.search_after_id = self.parent.after(300, func)
    
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Панель фильтрации (только для менеджера и админа)
        if self.user['role'] in ['manager', 'admin']:
            self.setup_filter_panel()
        
        # Таблица товаров
        self.setup_treeview()
        
        # Панель с кнопками
        self.setup_button_panel()
    
    def setup_filter_panel(self):
        """Панель фильтрации и поиска"""
        filter_frame = tk.Frame(self.parent, bg="#f8f9fa", height=80)
        filter_frame.pack(fill="x", padx=10, pady=10)
        filter_frame.pack_propagate(False)
        
        # Поиск
        tk.Label(filter_frame, text="🔍 Поиск:", bg="#f8f9fa", font=("Arial", 10)).grid(
            row=0, column=0, padx=(10,5), pady=10, sticky="w"
        )
        search_entry = ttk.Entry(
            filter_frame, 
            textvariable=self.search_var, 
            width=30,
            font=("Arial", 10)
        )
        search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        # Сортировка
        tk.Label(filter_frame, text="📊 Сортировка:", bg="#f8f9fa", font=("Arial", 10)).grid(
            row=0, column=2, padx=(20,5), pady=10, sticky="w"
        )
        
        sort_values = {
            "name_asc": "По названию (А-Я)",
            "name_desc": "По названию (Я-А)",
            "price_asc": "По цене (возр.)",
            "price_desc": "По цене (убыв.)",
            "quantity_asc": "По количеству (возр.)",
            "quantity_desc": "По количеству (убыв.)"
        }
        
        sort_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=list(sort_values.keys()),
            state="readonly",
            width=20
        )
        sort_combo.grid(row=0, column=3, padx=5, pady=10, sticky="w")
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Фильтр по поставщику
        tk.Label(filter_frame, text="🏭 Поставщик:", bg="#f8f9fa", font=("Arial", 10)).grid(
            row=1, column=0, padx=(10,5), pady=10, sticky="w"
        )
        
        suppliers = self.db.get_suppliers()
        supplier_values = ["all"] + [s['name'] for s in suppliers]
        
        self.supplier_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_supplier_var,
            values=supplier_values,
            state="readonly",
            width=25
        )
        self.supplier_combo.grid(row=1, column=1, columnspan=3, padx=5, pady=10, sticky="w")
        self.supplier_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
    
    def setup_treeview(self):
        """Создание таблицы товаров"""
        
        # Фрейм для таблицы и скроллбаров
        tree_frame = tk.Frame(self.parent)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Вертикальный скроллбар
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        
        # Горизонтальный скроллбар
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")
        
        # Колонки
        columns = (
            'id', 'name', 'category', 'manufacturer', 
            'supplier', 'price', 'discount', 'quantity', 'unit'
        )
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=20
        )
        
        # Настройка скроллбаров
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Заголовки
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Наименование')
        self.tree.heading('category', text='Категория')
        self.tree.heading('manufacturer', text='Производитель')
        self.tree.heading('supplier', text='Поставщик')
        self.tree.heading('price', text='Цена')
        self.tree.heading('discount', text='Скидка %')
        self.tree.heading('quantity', text='Кол-во')
        self.tree.heading('unit', text='Ед.')
        
        # Ширина колонок
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('name', width=200)
        self.tree.column('category', width=100)
        self.tree.column('manufacturer', width=120)
        self.tree.column('supplier', width=120)
        self.tree.column('price', width=80, anchor='e')
        self.tree.column('discount', width=70, anchor='center')
        self.tree.column('quantity', width=70, anchor='center')
        self.tree.column('unit', width=50, anchor='center')
        
        self.tree.pack(fill="both", expand=True)
        
        # Теги для форматирования
        self.tree.tag_configure('no_stock', background='#e3f2fd')  # Голубой
        self.tree.tag_configure('high_discount', background='#c8e6c9')  # Зеленый
        self.tree.tag_configure('discounted', foreground='red')
        
        # Привязываем события
        if self.user['role'] == 'admin':
            self.tree.bind('<Double-1>', self.edit_product)
    
    def setup_button_panel(self):
        """Панель с кнопками"""
        button_frame = tk.Frame(self.parent, bg="#f8f9fa", height=50)
        button_frame.pack(fill="x", side="bottom")
        button_frame.pack_propagate(False)
        
        # Кнопка обновления
        tk.Button(
            button_frame,
            text="🔄 Обновить",
            command=self.load_products,
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        ).pack(side="left", padx=10, pady=10)
        
        # Для администратора
        if self.user['role'] == 'admin':
            tk.Button(
                button_frame,
                text="➕ Добавить товар",
                command=self.add_product,
                bg="#27ae60",
                fg="white",
                font=("Arial", 10),
                cursor="hand2"
            ).pack(side="left", padx=5, pady=10)
            
            tk.Button(
                button_frame,
                text="🗑️ Удалить",
                command=self.delete_product,
                bg="#e74c3c",
                fg="white",
                font=("Arial", 10),
                cursor="hand2"
            ).pack(side="left", padx=5, pady=10)
        
        # Счетчик товаров
        self.count_label = tk.Label(
            button_frame,
            text="",
            bg="#f8f9fa",
            font=("Arial", 10)
        )
        self.count_label.pack(side="right", padx=20)
    
    def load_products(self):
        """Загрузка товаров из БД"""
        try:
            self.products = self.db.get_all_products()
            self.display_products(self.products)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить товары: {str(e)}")
    
    def display_products(self, products):
        """Отображение товаров в таблице"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем новыми данными
        for product in products:
            # Определяем теги для форматирования
            tags = []
            
            if product['quantity'] == 0:
                tags.append('no_stock')
            
            if product['discount'] > 15:
                tags.append('high_discount')
            
            # Форматирование цены со скидкой
            if product['discount'] > 0:
                final_price = product['price'] * (1 - product['discount'] / 100)
                price_display = f"~~{product['price']:.2f}~~ {final_price:.2f}"
                tags.append('discounted')
            else:
                price_display = f"{product['price']:.2f}"
            
            # Вставляем строку
            self.tree.insert(
                '',
                'end',
                values=(
                    product['id'],
                    product['name'],
                    product['category'],
                    product['manufacturer'],
                    product['supplier'],
                    price_display,
                    f"{product['discount']}%",
                    product['quantity'],
                    product['unit']
                ),
                tags=tags
            )
        
        # Обновляем счетчик
        self.count_label.config(text=f"Всего товаров: {len(products)}")
    
    def apply_filters(self, *args):
        """Применение фильтров"""
        if not hasattr(self, 'products'):
            return
        
        filtered = self.products.copy()
        
        # Поиск по тексту
        search_text = self.search_var.get().lower()
        if search_text:
            filtered = [
                p for p in filtered
                if search_text in p['name'].lower()
                or search_text in (p['description'] or '').lower()
                or search_text in p['category'].lower()
                or search_text in p['manufacturer'].lower()
                or search_text in p['supplier'].lower()
            ]
        
        # Фильтр по поставщику
        supplier_filter = self.filter_supplier_var.get()
        if supplier_filter and supplier_filter != "all":
            filtered = [
                p for p in filtered
                if p['supplier'] == supplier_filter
            ]
        
        # Сортировка
        sort_by = self.sort_var.get()
        if sort_by == "name_asc":
            filtered.sort(key=lambda x: x['name'])
        elif sort_by == "name_desc":
            filtered.sort(key=lambda x: x['name'], reverse=True)
        elif sort_by == "price_asc":
            filtered.sort(key=lambda x: x['price'])
        elif sort_by == "price_desc":
            filtered.sort(key=lambda x: x['price'], reverse=True)
        elif sort_by == "quantity_asc":
            filtered.sort(key=lambda x: x['quantity'])
        elif sort_by == "quantity_desc":
            filtered.sort(key=lambda x: x['quantity'], reverse=True)
        
        self.display_products(filtered)
    
    def edit_product(self, event):
        """Редактирование товара"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        product_id = values[0]
        
        from gui.product_edit import ProductEditWindow
        ProductEditWindow(
            self.parent.winfo_toplevel(),
            self.user,
            product_id=product_id,
            parent_window=self.main_window
        )
    
    def add_product(self):
        """Добавление товара"""
        from gui.product_edit import ProductEditWindow
        ProductEditWindow(
            self.parent.winfo_toplevel(),
            self.user,
            product_id=None,
            parent_window=self.main_window
        )
    
    def delete_product(self):
        """Удаление товара"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        product_id = values[0]
        product_name = values[1]
        
        if messagebox.askyesno(
            "Подтверждение",
            f"Удалить товар '{product_name}'?\nЭто действие нельзя отменить!"
        ):
            try:
                success = self.db.delete_product(product_id)
                if success:
                    self.load_products()
                    messagebox.showinfo("Успех", "Товар удален")
                else:
                    messagebox.showerror(
                        "Ошибка",
                        "Невозможно удалить товар, так как он есть в заказах"
                    )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить товар: {str(e)}")
    
    def refresh(self):
        """Обновление списка"""
        self.load_products()