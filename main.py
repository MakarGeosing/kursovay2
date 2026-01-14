import sys
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from auth.login_window import LoginWindow
from config import Config


def main():
    """Главная функция приложения"""
    try:
        app = QApplication(sys.argv)

        # Настройка шрифта
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(Config.FONT_SIZES['normal'])
        app.setFont(font)

        # Создаем окно входа
        window = LoginWindow()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()