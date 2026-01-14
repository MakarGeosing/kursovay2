from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import Database
from config import Config


class RegisterWindow(QDialog):
    """Окно регистрации"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Регистрация')
        self.setFixedSize(500, 450)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel('РЕГИСТРАЦИЯ')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["primary"]};
        ''')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Форма регистрации
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.username_input = self.create_input_field('Логин')
        self.password_input = self.create_input_field('Пароль', is_password=True)
        self.confirm_password_input = self.create_input_field('Повторите пароль', is_password=True)
        self.full_name_input = self.create_input_field('ФИО')

        form_layout.addRow('Логин:', self.username_input)
        form_layout.addRow('Пароль:', self.password_input)
        form_layout.addRow('Повторите пароль:', self.confirm_password_input)
        form_layout.addRow('ФИО:', self.full_name_input)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Сообщение об ошибке
        self.error_label = QLabel('')
        self.error_label.setStyleSheet(f'color: {Config.COLORS["danger"]}; font-size: {Config.FONT_SIZES["small"]}px;')
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        # Кнопки
        buttons_layout = QHBoxLayout()

        register_btn = QPushButton('Зарегистрироваться')
        register_btn.setMinimumHeight(45)
        register_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["success"]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        ''')
        register_btn.clicked.connect(self.register)

        cancel_btn = QPushButton('Отмена')
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["secondary"]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        ''')
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(register_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def create_input_field(self, placeholder, is_password=False):
        """Создание поля ввода"""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(40)
        if is_password:
            field.setEchoMode(QLineEdit.Password)

        field.setStyleSheet(f'''
            QLineEdit {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Config.COLORS["primary"]};
            }}
        ''')
        return field

    def register(self):
        """Обработка регистрации"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        full_name = self.full_name_input.text().strip()

        # Валидация
        if not username or not password or not confirm_password or not full_name:
            self.error_label.setText('Заполните все поля!')
            return

        if len(username) < 3:
            self.error_label.setText('Логин должен содержать минимум 3 символа')
            return

        if len(password) < 6:
            self.error_label.setText('Пароль должен содержать минимум 6 символов')
            return

        if password != confirm_password:
            self.error_label.setText('Пароли не совпадают!')
            return

        # Проверка существования username
        if not self.db.connect():
            self.error_label.setText('Ошибка подключения к базе данных')
            return

        if self.db.check_username_exists(username):
            self.error_label.setText('Пользователь с таким логином уже существует')
            self.db.disconnect()
            return

        # Регистрация
        if self.db.register_user(username, password, full_name):
            self.db.disconnect()
            QMessageBox.information(self, 'Успех', 'Регистрация прошла успешно! Теперь вы можете войти в систему.')
            self.accept()
        else:
            self.error_label.setText('Ошибка при регистрации')
            self.db.disconnect()