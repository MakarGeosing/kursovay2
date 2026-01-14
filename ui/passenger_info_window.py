from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from config import Config


class PassengerInfoWindow(QDialog):
    """Окно ввода данных пассажира"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Данные пассажира')
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel('ВВЕДИТЕ ДАННЫЕ ПАССАЖИРА')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["large"]}px;
            font-weight: bold;
            color: {Config.COLORS["primary"]};
        ''')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Поля формы
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.name_input = self.create_input_field('ФИО')
        self.document_input = self.create_input_field('Номер документа')
        self.phone_input = self.create_input_field('Телефон')

        form_layout.addRow('ФИО:', self.name_input)
        form_layout.addRow('Номер документа:', self.document_input)
        form_layout.addRow('Телефон:', self.phone_input)

        # Подсказка
        hint = QLabel('* Обязательные поля')
        hint.setStyleSheet(f'color: {Config.COLORS["danger"]}; font-size: {Config.FONT_SIZES["small"]}px;')
        form_layout.addRow('', hint)

        layout.addLayout(form_layout)
        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton('Сохранить')
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet(f'''
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
        save_btn.clicked.connect(self.validate_and_accept)

        cancel_btn = QPushButton('Отмена')
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["danger"]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        ''')
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def create_input_field(self, placeholder):
        """Создание поля ввода"""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(40)
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

    def validate_and_accept(self):
        """Валидация и закрытие окна"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите ФИО пассажира')
            self.name_input.setFocus()
            return

        if not self.document_input.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите номер документа')
            self.document_input.setFocus()
            return

        # Проверка формата телефона (простая)
        phone = self.phone_input.text().strip()
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')',
                                                                                                           '').isdigit():
            QMessageBox.warning(self, 'Ошибка', 'Введите корректный номер телефона')
            self.phone_input.setFocus()
            return

        self.accept()

    def get_passenger_data(self):
        """Получить данные пассажира"""
        return {
            'full_name': self.name_input.text().strip(),
            'document_number': self.document_input.text().strip(),
            'phone': self.phone_input.text().strip()
        }