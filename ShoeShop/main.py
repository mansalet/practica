#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Точка входа в приложение "Магазин обуви"
"""

import sys
import os

# Добавляем текущую папку в путь поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Создаем необходимые папки
os.makedirs('uploads', exist_ok=True)
os.makedirs('resources', exist_ok=True)

def main():
    """Главная функция"""
    
    # Создаем базу данных при первом запуске
    if not os.path.exists(os.path.join('database', 'shoe_shop.db')):
        print("🔄 Создание базы данных...")
        try:
            from database.create_db import create_database
            create_database()
            print("✅ База данных готова!")
        except Exception as e:
            print(f"❌ Ошибка создания БД: {e}")
            input("Нажмите Enter для выхода...")
            return
    
    # Запускаем приложение
    try:
        from gui.login_window import LoginWindow
        app = LoginWindow()
        app.run()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()