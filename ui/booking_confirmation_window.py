from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import Database
from config import Config


class BookingConfirmationWindow(QDialog):
    """Окно подтверждения бронирования"""

    def __init__(self, route_id, seat_id, passenger_data, user_id, parent=None):
        super().__init__(parent)
        self.route_id = route_id
        self.seat_id = seat_id
        self.passenger_data = passenger_data
        self.user_id = user_id
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Подтверждение бронирования')
        self.setFixedSize(600, 550)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel('ПОДТВЕРЖДЕНИЕ БРОНИРОВАНИЯ')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["large"]}px;
            font-weight: bold;
            color: {Config.COLORS["primary"]};
        ''')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Информация о бронировании
        info_frame = QFrame()
        info_frame.setStyleSheet('''
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
        ''')

        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        info_layout.setLabelAlignment(Qt.AlignRight)

        # Загружаем детали маршрута
        route_info = None
        if self.db.connect():
            query = """
            SELECT 
                r.departure_station,
                r.arrival_station,
                r.departure_time,
                r.arrival_time,
                r.base_price,
                t.train_name,
                t.train_number,
                s.seat_number,
                s.carriage_number,
                s.seat_type
            FROM routes r
            JOIN trains t ON r.train_id = t.id
            JOIN seats s ON s.id = %s
            WHERE r.id = %s
            """

            self.db.cursor.execute(query, (self.seat_id, self.route_id))
            route_info = self.db.cursor.fetchone()
            self.db.disconnect()

        if route_info:
            # Данные пассажира
            info_layout.addRow('ФИО:', QLabel(self.passenger_data['full_name']))
            info_layout.addRow('Документ:', QLabel(self.passenger_data['document_number']))
            info_layout.addRow('Телефон:', QLabel(self.passenger_data['phone']))

            info_layout.addItem(QSpacerItem(110, 110))

            # Данные о поездке
            info_layout.addRow('Поезд:', QLabel(f"{route_info['train_name']} ({route_info['train_number']})"))
            info_layout.addRow('Маршрут:',
                               QLabel(f"{route_info['departure_station']} → {route_info['arrival_station']}"))
            info_layout.addRow('Отправление:', QLabel(route_info['departure_time'].strftime('%d.%m.%Y %H:%M')))
            info_layout.addRow('Прибытие:', QLabel(route_info['arrival_time'].strftime('%d.%m.%Y %H:%M')))
            info_layout.addRow('Место:',
                               QLabel(f"Вагон {route_info['carriage_number']}, Место {route_info['seat_number']}"))
            info_layout.addRow('Тип места:', QLabel(route_info['seat_type']))
            info_layout.addRow('Цена:', QLabel(f"{route_info['base_price']:.2f} ₽"))
        else:
            info_layout.addRow('Ошибка:', QLabel('Не удалось загрузить информацию'))

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # Оплата
        payment_group = QGroupBox('Способ оплаты')
        payment_group.setStyleSheet(f'''
            QGroupBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                color: {Config.COLORS["dark"]};
                padding: 0 10px;
            }}
        ''')

        payment_layout = QVBoxLayout()

        self.cash_radio = QRadioButton('Наличные (оплата при получении)')
        self.card_radio = QRadioButton('Банковская карта (оплата сейчас)')
        self.card_radio.setChecked(True)

        payment_layout.addWidget(self.cash_radio)
        payment_layout.addWidget(self.card_radio)
        payment_group.setLayout(payment_layout)

        layout.addWidget(payment_group)

        # Примечание
        note = QLabel('* При оплате картой необходимо дополнительное подтверждение администратора')
        note.setStyleSheet(
            f'color: {Config.COLORS["dark"]}; font-size: {Config.FONT_SIZES["small"]}px; font-style: italic;')
        layout.addWidget(note)

        # Кнопки
        buttons_layout = QHBoxLayout()

        confirm_btn = QPushButton('✅ Подтвердить бронирование')
        confirm_btn.setMinimumHeight(50)
        confirm_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["success"]};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        ''')
        confirm_btn.clicked.connect(self.confirm_booking)

        cancel_btn = QPushButton('Отмена')
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["danger"]};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        ''')
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(confirm_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def confirm_booking(self):
        """Подтверждение бронирования"""
        try:
            if self.db.connect():
                booking_id = self.db.create_booking(self.passenger_data, self.seat_id, self.route_id, self.user_id)
                self.db.disconnect()

                if booking_id:
                    # Определяем способ оплаты
                    payment_method = "наличные" if self.cash_radio.isChecked() else "карта"

                    if payment_method == "карта":
                        # Пользователь оплатил картой, но нужна проверка админа
                        message = (f'Бронирование №{booking_id} успешно создано!\n'
                                   f'Способ оплаты: {payment_method}\n'
                                   f'Сумма: {self.get_booking_price()} ₽\n\n'
                                   f'⚠️ Для завершения бронирования необходимо:\n'
                                   f'1. Оплатить бронирование в разделе "Мои бронирования"\n'
                                   f'2. Дождаться подтверждения администратора')
                    else:
                        # Пользователь выбрал наличные
                        message = (f'Бронирование №{booking_id} успешно создано!\n'
                                   f'Способ оплаты: {payment_method}\n'
                                   f'Сумма: {self.get_booking_price()} ₽\n\n'
                                   f'⏳ Ожидайте подтверждения оплаты администратором')

                    QMessageBox.information(self, 'Успех', message)
                    self.accept()
                else:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось создать бронирование. Возможно, место уже занято.')
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}')

    def get_booking_price(self):
        """Получить цену бронирования"""
        if self.db.connect():
            query = "SELECT base_price FROM routes WHERE id = %s"
            self.db.cursor.execute(query, (self.route_id,))
            result = self.db.cursor.fetchone()
            self.db.disconnect()
            return f"{result['base_price']:.2f}" if result else "0.00"
        return "0.00"