import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Тестирование импортов...")

    # Пробуем импортировать все модули
    from database import Database

    print("✓ database.py импортирован")

    from config import Config

    print("✓ config.py импортирован")

    from models import User

    print("✓ models.py импортирован")

    from auth.login_window import LoginWindow

    print("✓ login_window.py импортирован")

    from auth.register_window import RegisterWindow

    print("✓ register_window.py импортирован")

    from ui.main_window import MainWindow

    print("✓ main_window.py импортирован")

    from ui.routes_page import SearchPage

    print("✓ routes_page.py импортирован")

    from ui.bookings_page import BookingsPage

    print("✓ bookings_page.py импортирован")

    from ui.admin_page import AdminPage

    print("✓ admin_page.py импортирован")

    from ui.routes_management_page import RoutesManagementPage

    print("✓ routes_management_page.py импортирован")

    print("\n✅ Все импорты работают корректно!")

except Exception as e:
    print(f"\n❌ Ошибка импорта: {e}")
    import traceback

    print(traceback.format_exc())