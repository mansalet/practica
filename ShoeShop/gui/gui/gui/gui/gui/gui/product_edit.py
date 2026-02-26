import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from PIL import Image, ImageTk
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db_models import Database

class ProductEditWindow:
    """Окно редактирования товара"""
    
    def __init__(self, parent, user, product_id=None, parent_window=None):
        self.user = user
        self.product_id = product_id
        self.parent_window = parent_window
        self.db = Database()
        self.photo_path = None
        self.old_photo_path = None
        
        # Проверка прав
        if user['role'] != 'admin':
            messagebox.showerror("Ошибка", "Только администратор может редактировать товары")
            return
        
        # Создание окна
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление товара" if not product_id else "Редактирование товара")
        self.window.geometry("650x750")
        self.window.resizable(False, False)
        self.window.grab_set()  # Модальное окно
        self.window.focus_set()
        
        # Центрируем
        self.center_window()
        
        # Загружаем справочники
        self.load_reference_data()
        
        # Создаем интерфейс
        self.setup_ui()
        
        # Если редактирование - загружаем данные
        if product_id:
            self.load_product_data()
        
        # Обработка закрытия
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Центрирование окна"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
    
    def load_reference_data(self):
        """Загрузка справочников"""
        self.categories = self.db.get_categories()
        self.manufacturers = self.db.get_manufacturers()
        self.suppliers = self.db.get_suppliers()
        self.units = self.db.get_units()
    
    def setup_ui(self):
        """Создание интерфейса"""
        
        # Основной фрейм
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # ID товара (при редактировании)
        if self.product_id:
            id_frame = ttk.Frame(main_frame)
            id_frame.pack(fill="x", pady=5)
            
            ttk.Label(id_frame, text="ID товара:", font=("Arial", 10, "bold")).pack(side="left")
            ttk.Label(id_frame, text=str(self.product_id), font=("Arial", 10)).pack(side="left", padx=10)
        
        # Фото
        self.setup_photo_section(main_frame)
        
        # Поля ввода
        self.setup_fields(main_frame)
        
        # Кнопки
        self.setup_buttons(main_frame)
    
    def setup_photo_section(self, parent):
        """Секция загрузки фото"""
        photo_frame = ttk.LabelFrame(parent, text="Фото товара", padding="10")
        photo_frame.pack(fill="x", pady=10)
        
        # Контейнер для фото
        photo_container = ttk.Frame(photo_frame)
        photo_container.pack(fill="x")
        
        # Метка для фото
        self.photo_label = ttk.Label(photo_container, relief="solid", width=30, height=15)
        self.photo_label.pack(side="left", padx=10)
        
        # Кнопки
        btn_frame = ttk.Frame(photo_container)
        btn_frame.pack(side="left", padx=20)
        
        ttk.Button(
            btn_frame,
            text="📷 Загрузить фото",
            command=self.load_photo,
            width=20
        ).pack(pady=5)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Удалить фото",
            command=self.delete_photo,
            width=20
        ).pack(pady=5)
        
        # Информация
        ttk.Label(
            photo_frame,
            text="Рекомендуемый размер: 300x200 пикселей",
            font=("Arial", 8),
            foreground="gray"
        ).pack(pady=5)
        
        # Показываем заглушку
        self.show_placeholder()
    
    def setup_fields(self, parent):
        """Создание полей ввода"""
        fields_frame = ttk.LabelFrame(parent, text="Информация о товаре", padding="10")
        fields_frame.pack(fill="both", expand=True, pady=10)
        
        # Словарь для хранения полей
        self.entries = {}
        
        # Создаем поля с помощью grid
        row = 0
        
        # Наименование
        ttk.Label(fields_frame, text="Наименование *").grid(
            row=row, column=0, sticky="w", pady=5
        )
        self.entries['name'] = ttk.Entry(fields_frame, width=40)
        self.entries['name'].grid(row=row, column=1, sticky="w", pady=5, padx=10)
        row += 1
        
        # Категория
        ttk.Label(fields_frame, text="Категория").grid(
            row=row, column=0, sticky="w", pady=5
        )
        self.entries['category'] = ttk.Combobox(
            fields_frame,
            values=[c['name'] for c in self.categories],
            state="readonly",
            width=38
        )
        self.entries['category'].grid(row=row, column=1, sticky="w", pady=5, padx=10)
        row += 1
        
        # Производитель
        ttk.Label(fields_frame, text="Производитель").grid(
            row=row, column=0, sticky="w", pady=5
        )
        self.entries['manufacturer'] = ttk.Combobox(
            fields_frame,
            values=[m['name'] for m in self.manufacturers],
            state="readonly",
            width=38
        )
        self.entries['manufacturer'].grid(row=row, column=1, sticky="w", pady=5, padx=10)
        row += 1
        
        # Поставщик
        ttk.Label(fields_frame, text="Поставщик").grid(
            row=row, column=0, sticky="w", pady=5
        )
        self.entries['supplier'] = ttk.Combobox(
            fields_frame,
            values=[s['name'] for s in self.suppliers],
            state="readonly",
            width=38
        )
        self.entries['supplier'].grid(row=row, column=1, sticky="w", pady=5, padx=10)
        row += 1
        
        # Цена
        ttk.Label(fields_frame, text="Цена (₽) *").grid(
            row=row, column=0, sticky="w", pady=5
        )
        price_frame = ttk.Frame(fields_frame)
        price_frame.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        
        self.entries['price'] = ttk.Entry(price_frame, width=15)
        self.entries['price'].pack(side="left")
        ttk.Label(price_frame, text="(не может быть отрицательной)").pack(side="left", padx=5)
        row += 1
        
        # Скидка
        ttk.Label(fields_frame, text="Скидка (%)").grid(
            row=row, column=0, sticky="w", pady=5
        )
        discount_frame = ttk.Frame(fields_frame)
        discount_frame.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        
        self.entries['discount'] = ttk.Entry(discount_frame, width=10)
        self.entries['discount'].pack(side="left")
        ttk.Label(discount_frame, text="(0-100)").pack(side="left", padx=5)
        row += 1
        
        # Единица измерения
        ttk.Label(fields_frame, text="Единица измерения").grid(
            row=row, column=0, sticky="w", pady=5
        )
        self.entries['unit'] = ttk.Combobox(
            fields_frame,
            values=[f"{u['name']} ({u['short_name']})" for u in self.units],
            state="readonly",
            width=38
        )
        self.entries['unit'].grid(row=row, column=1, sticky="w", pady=5, padx=10)
        row += 1
        
        # Количество
        ttk.Label(fields_frame, text="Количество на складе").grid(
            row=row, column=0, sticky="w", pady=5
        )
        quantity_frame = ttk.Frame(fields_frame)
        quantity_frame.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        
        self.entries['quantity'] = ttk.Entry(quantity_frame, width=10)
        self.entries['quantity'].pack(side="left")
        ttk.Label(quantity_frame, text="(целое число)").pack(side="left", padx=5)
        row += 1
        
        # Описание
        ttk.Label(fields_frame, text="Описание").grid(
            row=row, column=0, sticky="nw", pady=5
        )
        
        desc_frame = ttk.Frame(fields_frame)
        desc_frame.grid(row=row, column=1, sticky="w", pady=5, padx=10)
        
        self.entries['description'] = tk.Text(desc_frame, width=38, height=5, wrap="word")
        self.entries['description'].pack(side="left")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=self.entries['description'].yview)
        scrollbar.pack(side="right", fill="y")
        self.entries['description'].configure(yscrollcommand=scrollbar.set)
        row += 1
        
        # Подсказка
        ttk.Label(
            fields_frame,
            text="* - обязательные поля",
            font=("Arial", 8),
            foreground="red"
        ).grid(row=row, column=0, columnspan=2, pady=10)
    
    def setup_buttons(self, parent):
        """Кнопки сохранения"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            button_frame,
            text="💾 Сохранить",
            command=self.save_product,
            width=15
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="✖ Отмена",
            command=self.on_closing,
            width=15
        ).pack(side="left", padx=5)
    
    def show_placeholder(self):
        """Показать заглушку фото"""
        try:
            # Пробуем загрузить заглушку
            placeholder = "resources/picture.png"
            if os.path.exists(placeholder):
                img = Image.open(placeholder)
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=photo)
                self.photo_label.image = photo
            else:
                # Если нет файла - цветной прямоугольник
                self.photo_label.config(text="Нет фото", background="#f0f0f0")
        except Exception as e:
            print(f"Ошибка загрузки заглушки: {e}")
            self.photo_label.config(text="Ошибка", background="#ffcccc")
    
    def load_photo(self):
        """Загрузка фото"""
        file_path = filedialog.askopenfilename(
            title="Выберите фото",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Открываем изображение
            img = Image.open(file_path)
            
            # Ресайз до 300x200
            img = img.resize((300, 200), Image.Resampling.LANCZOS)
            
            # Генерируем имя файла
            import time
            filename = f"product_{int(time.time())}.jpg"
            save_path = os.path.join("uploads", filename)
            
            # Сохраняем
            img.save(save_path, "JPEG", quality=85)
            
            # Обновляем путь
            if self.photo_path and not self.old_photo_path:
                self.old_photo_path = self.photo_path
            self.photo_path = save_path
            
            # Показываем в интерфейсе
            display_img = img.resize((150, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_img)
            self.photo_label.config(image=photo)
            self.photo_label.image = photo
            
            messagebox.showinfo("Успех", "Фото загружено")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить фото: {str(e)}")
    
    def delete_photo(self):
        """Удаление фото"""
        if self.photo_path and os.path.exists(self.photo_path):
            if messagebox.askyesno("Подтверждение", "Удалить фото?"):
                try:
                    os.remove(self.photo_path)
                    self.photo_path = None
                    self.show_placeholder()
                    messagebox.showinfo("Успех", "Фото удалено")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить фото: {str(e)}")
    
    def load_product_data(self):
        """Загрузка данных товара"""
        product = self.db.get_product_by_id(self.product_id)
        
        if not product:
            messagebox.showerror("Ошибка", "Товар не найден")
            self.on_closing()
            return
        
        # Заполняем поля
        self.entries['name'].insert(0, product['name'] or "")
        
        # Категория
        if product['category_id']:
            cat = next((c for c in self.categories if c['id'] == product['category_id']), None)
            if cat:
                self.entries['category'].set(cat['name'])
        
        # Производитель
        if product['manufacturer_id']:
            man = next((m for m in self.manufacturers if m['id'] == product['manufacturer_id']), None)
            if man:
                self.entries['manufacturer'].set(man['name'])
        
        # Поставщик
        if product['supplier_id']:
            sup = next((s for s in self.suppliers if s['id'] == product['supplier_id']), None)
            if sup:
                self.entries['supplier'].set(sup['name'])
        
        # Цена
        self.entries['price'].insert(0, str(product['price']))
        
        # Скидка
        if product['discount']:
            self.entries['discount'].insert(0, str(product['discount']))
        
        # Единица измерения
        if product['unit_id']:
            unit = next((u for u in self.units if u['id'] == product['unit_id']), None)
            if unit:
                self.entries['unit'].set(f"{unit['name']} ({unit['short_name']})")
        
        # Количество
        self.entries['quantity'].insert(0, str(product['quantity']))
        
        # Описание
        if product['description']:
            self.entries['description'].insert("1.0", product['description'])
        
        # Фото
        if product['photo_path'] and os.path.exists(product['photo_path']):
            self.photo_path = product['photo_path']
            try:
                img = Image.open(product['photo_path'])
                img = img.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_label.config(image=photo)
                self.photo_label.image = photo
            except Exception as e:
                print(f"Ошибка загрузки фото: {e}")
    
    def validate(self):
        """Проверка полей"""
        errors = []
        
        # Наименование
        if not self.entries['name'].get().strip():
            errors.append("Наименование товара обязательно")
        
        # Цена
        try:
            price = float(self.entries['price'].get().strip())
            if price < 0:
                errors.append("Цена не может быть отрицательной")
        except ValueError:
            errors.append("Цена должна быть числом")
        
        # Скидка
        disc = self.entries['discount'].get().strip()
        if disc:
            try:
                d = float(disc)
                if d < 0 or d > 100:
                    errors.append("Скидка должна быть от 0 до 100")
            except ValueError:
                errors.append("Скидка должна быть числом")
        
        # Количество
        qty = self.entries['quantity'].get().strip()
        if qty:
            try:
                q = int(qty)
                if q < 0:
                    errors.append("Количество не может быть отрицательным")
            except ValueError:
                errors.append("Количество должно быть целым числом")
        
        return errors
    
    def save_product(self):
        """Сохранение товара"""
        
        # Валидация
        errors = self.validate()
        if errors:
            messagebox.showerror(
                "Ошибка ввода",
                "Исправьте ошибки:\n\n" + "\n".join(errors)
            )
            return
        
        try:
            # Собираем данные
            data = {
                'name': self.entries['name'].get().strip(),
                'description': self.entries['description'].get("1.0", "end-1c").strip(),
                'price': float(self.entries['price'].get().strip()),
                'discount': float(self.entries['discount'].get().strip() or 0),
                'quantity': int(self.entries['quantity'].get().strip() or 0),
                'photo_path': self.photo_path,
                'manufacturer_id': None,
                'supplier_id': None,
                'category_id': None,
                'unit_id': None
            }
            
            # Получаем ID из выпадающих списков
            cat_name = self.entries['category'].get()
            if cat_name:
                cat = next((c for c in self.categories if c['name'] == cat_name), None)
                if cat:
                    data['category_id'] = cat['id']
            
            man_name = self.entries['manufacturer'].get()
            if man_name:
                man = next((m for m in self.manufacturers if m['name'] == man_name), None)
                if man:
                    data['manufacturer_id'] = man['id']
            
            sup_name = self.entries['supplier'].get()
            if sup_name:
                sup = next((s for s in self.suppliers if s['name'] == sup_name), None)
                if sup:
                    data['supplier_id'] = sup['id']
            
            unit_text = self.entries['unit'].get()
            if unit_text:
                unit_name = unit_text.split(' (')[0]
                unit = next((u for u in self.units if u['name'] == unit_name), None)
                if unit:
                    data['unit_id'] = unit['id']
            
            # Сохраняем
            if self.product_id:
                # Удаляем старое фото если нужно
                if self.old_photo_path and os.path.exists(self.old_photo_path):
                    try:
                        os.remove(self.old_photo_path)
                    except:
                        pass
                
                self.db.update_product(self.product_id, data)
                messagebox.showinfo("Успех", "Товар обновлен")
            else:
                new_id = self.db.add_product(data)
                # Переименовываем временное фото
                if self.photo_path and 'temp_' not in self.photo_path:
                    new_path = os.path.join("uploads", f"product_{new_id}.jpg")
                    try:
                        os.rename(self.photo_path, new_path)
                        data['photo_path'] = new_path
                        self.db.update_product(new_id, data)
                    except:
                        pass
                messagebox.showinfo("Успех", "Товар добавлен")
            
            # Обновляем список
            if self.parent_window:
                self.parent_window.refresh_products()
            
            self.on_closing()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def on_closing(self):
        """Закрытие окна"""
        # Удаляем временные фото
        if self.photo_path and 'temp_' in self.photo_path and os.path.exists(self.photo_path):
            try:
                os.remove(self.photo_path)
            except:
                pass
        
        self.window.destroy()