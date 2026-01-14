from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import Database
from config import Config
from auth.register_window import RegisterWindow


class LoginWindow(QWidget):
    """Окно авторизации"""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        # Настройки окна
        self.setWindowTitle('Авторизация - РЖД')
        self.setFixedSize(1100, 900)

        # Основной layout
        layout = QVBoxLayout()
        layout.setContentsMargins(110, 110, 110, 110)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel('ВХОД В СИСТЕМУ')
        title_font = QFont()
        title_font.setPointSize(Config.FONT_SIZES['title'])
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f'color: {Config.COLORS["primary"]}; margin-bottom: 30px;')
        layout.addWidget(title)

        # Иконка
        icon = QLabel('🚆')
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet('font-size: 60px; margin-bottom: 20px;')
        layout.addWidget(icon)

        # Форма входа
        form_group = QGroupBox('Данные для входа')
        form_group.setStyleSheet(f'''
            QGroupBox {{
                font-size: {Config.FONT_SIZES["large"]}px;
                font-weight: bold;
                border: 2px solid {Config.COLORS["primary"]};
                border-radius: 8px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                color: {Config.COLORS["primary"]};
                padding: 0 10px;
            }}
        ''')

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Поле логина
        self.username_input = self.create_input_field('Логин:', 'admin')
        form_layout.addWidget(self.username_input)

        # Поле пароля
        self.password_input = self.create_input_field('Пароль:', 'admin123', is_password=True)
        form_layout.addWidget(self.password_input)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.login_btn = self.create_button('ВОЙТИ В СИСТЕМУ', self.login)

        register_btn = QPushButton('📝 Регистрация')
        register_btn.setMinimumHeight(50)
        register_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["secondary"]};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        ''')
        register_btn.clicked.connect(self.show_register_window)

        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(register_btn)

        layout.addLayout(buttons_layout)

        # Информация о тестовых пользователях
        info = QLabel('Тестовые данные:\n'
                      'Логин: admin / Пароль: admin123 (Администратор)\n'
                      'Логин: test_user / Пароль: test123 (Пользователь)')
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet(f'''
            color: #666;
            font-size: {Config.FONT_SIZES["small"]}px;
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 8px;
        ''')
        layout.addWidget(info)

        layout.addStretch()
        self.setLayout(layout)

        # Фокус
        self.username_input.findChild(QLineEdit).setFocus()

    def create_input_field(self, label_text, placeholder, is_password=False):
        """Создание поля ввода"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        label = QLabel(label_text)
        label.setStyleSheet(f'font-weight: bold; font-size: {Config.FONT_SIZES["normal"]}px;')
        layout.addWidget(label)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(45)
        if is_password:
            field.setEchoMode(QLineEdit.Password)
            field.setText(placeholder)
        else:
            field.setText(placeholder)

        field.setStyleSheet(f'''
            QLineEdit {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Config.COLORS["primary"]};
            }}
        ''')
        layout.addWidget(field)

        widget.setLayout(layout)
        return widget

    def create_button(self, text, handler):
        """Создание кнопки"""
        btn = QPushButton(text)
        btn.setMinimumHeight(55)
        btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {Config.FONT_SIZES["xlarge"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #b71c1c;
            }}
        ''')
        btn.clicked.connect(handler)
        return btn

    def login(self):
        """Обработка входа"""
        username = self.username_input.findChild(QLineEdit).text().strip()
        password = self.password_input.findChild(QLineEdit).text().strip()

        if not username or not password:
            self.show_error('Заполните все поля!')
            return

        # Подключаемся к БД
        if not self.db.connect():
            self.show_error('Ошибка подключения к базе данных')
            return

        # Аутентификация
        user = self.db.authenticate_user(username, password)
        self.db.disconnect()

        if user:
            self.show_success(user)
        else:
            self.show_error('Неверный логин или пароль!')

    def show_register_window(self):
        """Показать окно регистрации"""
        register_window = RegisterWindow(self)
        if register_window.exec_() == QDialog.Accepted:
            QMessageBox.information(self, 'Успех', 'Регистрация прошла успешно! Теперь вы можете войти.')

    def show_error(self, message):
        """Показать ошибку"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Ошибка')
        msg.setText(message)
        msg.exec_()

    def show_success(self, user):
        """Показать успешный вход"""
        try:
            # Импортируем здесь, чтобы избежать циклических импортов
            from ui.main_window import MainWindow

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle('Успешно')

            # Проверяем роль пользователя
            if user.role == 'user':
                msg.setText(f'Добро пожаловать, {user.full_name}!')
            elif user.role == 'admin':
                msg.setText(f'Добро пожаловать, {user.full_name}! Вы вошли как администратор.')

            msg.exec_()

            # Закрываем окно входа и открываем главное
            self.close()
            self.main_window = MainWindow(user)
            self.main_window.show()

        except Exception as e:
            # Если есть ошибка, показываем её
            QMessageBox.critical(self, 'Ошибка', f'Не удалось открыть главное окно: {str(e)}')
            import traceback
            print(traceback.format_exc())