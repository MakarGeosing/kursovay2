from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import Database
from config import Config
from ui.routes_management_page import RoutesManagementPage


class AdminPage(QWidget):
    """Страница администратора"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel('ПАНЕЛЬ АДМИНИСТРАТОРА')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xxlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["dark"]};
            margin-bottom: 10px;
        ''')
        layout.addWidget(title)

        # Вкладки
        self.tab_widget = QTabWidget()

        # Вкладка управления рейсами
        self.routes_management_page = RoutesManagementPage(self.user)
        self.tab_widget.addTab(self.routes_management_page, '🚆 Управление рейсами')

        # Вкладка бронирований
        self.bookings_tab = self.create_bookings_tab()
        self.tab_widget.addTab(self.bookings_tab, '📋 Все бронирования')

        # Вкладка пользователей
        self.users_tab = self.create_users_tab()
        self.tab_widget.addTab(self.users_tab, '👥 Управление пользователями')

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def create_bookings_tab(self):
        """Создание вкладки бронирований"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Панель управления
        control_layout = QHBoxLayout()

        refresh_btn = QPushButton('🔄 Обновить')
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["secondary"]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {Config.FONT_SIZES["normal"]}px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        ''')
        refresh_btn.clicked.connect(self.load_all_bookings)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            ['Все бронирования', 'Оплаченные (ожидают подтверждения)', 'Подтвержденные', 'Отмененные',
             'Забронированные'])
        self.filter_combo.setMinimumHeight(40)
        self.filter_combo.setStyleSheet(f'''
            QComboBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}
        ''')
        self.filter_combo.currentTextChanged.connect(self.load_all_bookings)

        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(QLabel('Фильтр:'))
        control_layout.addWidget(self.filter_combo)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Таблица бронирований
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(10)
        self.bookings_table.setHorizontalHeaderLabels([
            'ID', 'Пассажир', 'Поезд', 'Маршрут', 'Отправление',
            'Пользователь', 'Статус', 'Цена', 'Подтверждено', 'Действия'
        ])
        self.bookings_table.horizontalHeader().setStretchLastSection(True)
        self.bookings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bookings_table.setSelectionMode(QAbstractItemView.SingleSelection)

        layout.addWidget(self.bookings_table)

        widget.setLayout(layout)

        # Загружаем данные
        self.load_all_bookings()

        return widget

    def create_users_tab(self):
        """Создание вкладки пользователей"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Панель управления
        control_layout = QHBoxLayout()

        refresh_btn = QPushButton('🔄 Обновить')
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["secondary"]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {Config.FONT_SIZES["normal"]}px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        ''')
        refresh_btn.clicked.connect(self.load_all_users)

        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            'ID', 'Логин', 'ФИО', 'Роль', 'Дата регистрации', 'Действия'
        ])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setSelectionMode(QAbstractItemView.SingleSelection)

        layout.addWidget(self.users_table)

        widget.setLayout(layout)

        # Загружаем данные
        self.load_all_users()

        return widget

    def load_all_bookings(self):
        """Загрузка всех бронирований"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        all_bookings = self.db.get_all_bookings()
        self.db.disconnect()

        if not all_bookings:
            self.bookings_table.setRowCount(0)
            return

        # Фильтруем бронирования
        filter_text = self.filter_combo.currentText()
        if filter_text == 'Оплаченные (ожидают подтверждения)':
            bookings = [b for b in all_bookings if
                        (b['status'] == 'оплачен' or b['status'] == 'paid') and  # Добавлено 'paid'
                        not b['confirmed_by_admin']]
        elif filter_text == 'Подтвержденные':
            bookings = [b for b in all_bookings if b['confirmed_by_admin']]
        elif filter_text == 'Отмененные':
            bookings = [b for b in all_bookings if b['status'] in ['отменено', 'canceled']]  # Добавлено 'canceled'
        elif filter_text == 'Забронированные':
            bookings = [b for b in all_bookings if b['status'] in ['забронирован', 'booked']]  # Добавлено 'booked'
        else:
            bookings = all_bookings

        # Заполняем таблицу
        self.bookings_table.setRowCount(len(bookings))

        for row, booking in enumerate(bookings):
            self.bookings_table.setItem(row, 0, QTableWidgetItem(str(booking['booking_id'])))
            self.bookings_table.setItem(row, 1, QTableWidgetItem(booking['full_name']))
            self.bookings_table.setItem(row, 2,
                                        QTableWidgetItem(f"{booking['train_name']} ({booking['train_number']})"))

            route = f"{booking['departure_station']} → {booking['arrival_station']}"
            self.bookings_table.setItem(row, 3, QTableWidgetItem(route))

            departure = booking['departure_time'].strftime('%d.%m.%Y %H:%M')
            self.bookings_table.setItem(row, 4, QTableWidgetItem(departure))

            self.bookings_table.setItem(row, 5,
                                        QTableWidgetItem(f"{booking['user_full_name']} ({booking['created_by_user']})"))

            # Статус - нормализуем строки статуса
            status = booking['status'].lower() if booking['status'] else ''
            confirmed = booking['confirmed_by_admin']

            if confirmed:
                status_text = '✅ Подтверждено'
            elif status in ['оплачен', 'paid', 'payment']:
                status_text = '💰 Оплачено'
            elif status in ['забронирован', 'booked', 'reserved']:
                status_text = '⏳ Забронировано'
            elif status in ['отменено', 'canceled', 'cancelled']:
                status_text = '❌ Отменено'
            else:
                status_text = booking['status']  # Оставляем оригинальный текст

            status_item = QTableWidgetItem(status_text)
            if 'Подтверждено' in status_text:
                status_item.setBackground(QColor(220, 255, 220))
            elif 'Оплачено' in status_text:
                status_item.setBackground(QColor(255, 255, 200))
            elif 'Забронировано' in status_text:
                status_item.setBackground(QColor(255, 245, 200))
            else:
                status_item.setBackground(QColor(255, 220, 220))

            self.bookings_table.setItem(row, 6, status_item)

            self.bookings_table.setItem(row, 7, QTableWidgetItem(f"{booking['final_price']:.2f} ₽"))

            # Подтверждено админом
            confirmed_item = QTableWidgetItem('✅ Да' if confirmed else '❌ Нет')
            self.bookings_table.setItem(row, 8, confirmed_item)

            # Действия
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)

            # Показываем кнопку подтверждения для всех НЕ подтвержденных бронирований,
            # кроме отмененных
            if not confirmed and status not in ['отменено', 'canceled', 'cancelled']:
                confirm_btn = QPushButton('✅ Подтвердить')
                confirm_btn.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {Config.COLORS["success"]};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px;
                        font-size: {Config.FONT_SIZES["small"]}px;
                    }}
                    QPushButton:hover {{
                        background-color: #45a049;
                    }}
                ''')
                confirm_btn.clicked.connect(lambda checked, bid=booking['booking_id']: self.confirm_booking(bid))
                actions_layout.addWidget(confirm_btn)

            view_btn = QPushButton('👁 Просмотр')
            view_btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: {Config.COLORS["secondary"]};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: {Config.FONT_SIZES["small"]}px;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
            ''')
            view_btn.clicked.connect(lambda checked, bid=booking['booking_id']: self.view_booking_details(bid))
            actions_layout.addWidget(view_btn)

            if status in ['забронирован', 'booked', 'reserved', 'оплачен', 'paid']:
                cancel_btn = QPushButton('❌ Отменить')
                cancel_btn.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {Config.COLORS["danger"]};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px;
                        font-size: {Config.FONT_SIZES["small"]}px;
                    }}
                    QPushButton:hover {{
                        background-color: #d32f2f;
                    }}
                ''')
                cancel_btn.clicked.connect(lambda checked, bid=booking['booking_id']: self.cancel_booking(bid))
                actions_layout.addWidget(cancel_btn)

            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.bookings_table.setCellWidget(row, 9, actions_widget)

    def load_all_users(self):
        """Загрузка всех пользователей"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        users = self.db.get_all_users()
        self.db.disconnect()

        if not users:
            self.users_table.setRowCount(0)
            return

        # Заполняем таблицу
        self.users_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.users_table.setItem(row, 2, QTableWidgetItem(user['full_name']))

            # Роль
            role_item = QTableWidgetItem(user['role'])
            if user['role'] == 'admin':
                role_item.setBackground(QColor(255, 220, 220))
            else:
                role_item.setBackground(QColor(220, 255, 220))
            self.users_table.setItem(row, 3, role_item)

            # Дата регистрации
            date = user['created_at'].strftime('%d.%m.%Y %H:%M')
            self.users_table.setItem(row, 4, QTableWidgetItem(date))

            # Действия
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)

            if user['id'] != self.user.id:  # Нельзя менять свою роль
                role_combo = QComboBox()
                role_combo.addItems(['user', 'admin'])
                role_combo.setCurrentText(user['role'])
                role_combo.setProperty('user_id', user['id'])
                role_combo.currentTextChanged.connect(self.change_user_role)

                actions_layout.addWidget(role_combo)

            actions_layout.addStretch()
            actions_widget.setLayout(actions_layout)
            self.users_table.setCellWidget(row, 5, actions_widget)

    def confirm_booking(self, booking_id):
        """Подтверждение бронирования администратором"""
        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Подтвердить бронирование №{booking_id}?',
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db.connect():
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                return

            if self.db.confirm_booking(booking_id):
                QMessageBox.information(self, 'Успех', 'Бронирование успешно подтверждено')
                self.load_all_bookings()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подтвердить бронирование')

            self.db.disconnect()

    def view_booking_details(self, booking_id):
        """Просмотр деталей бронирования"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        details = self.db.get_booking_details(booking_id)
        self.db.disconnect()

        if details:
            self.show_booking_details(details)

    def show_booking_details(self, details):
        """Показать детали бронирования"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Детали бронирования №{details["booking_id"]}')
        dialog.setFixedSize(500, 650)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel(f'БРОНИРОВАНИЕ №{details["booking_id"]}')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["large"]}px;
            font-weight: bold;
            color: {Config.COLORS["primary"]};
        ''')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Информация
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

        # Пассажир
        info_layout.addRow('<b>ПАССАЖИР:</b>', QLabel(''))
        info_layout.addRow('ФИО:', QLabel(details['full_name']))
        info_layout.addRow('Документ:', QLabel(details['document_number']))
        info_layout.addRow('Телефон:', QLabel(details['phone']))

        info_layout.addItem(QSpacerItem(20, 10))

        # Поездка
        info_layout.addRow('<b>ПОЕЗДКА:</b>', QLabel(''))
        info_layout.addRow('Поезд:', QLabel(f"{details['train_name']} ({details['train_number']})"))
        info_layout.addRow('Маршрут:', QLabel(f"{details['departure_station']} → {details['arrival_station']}"))
        info_layout.addRow('Отправление:', QLabel(details['departure_time'].strftime('%d.%m.%Y %H:%M')))
        info_layout.addRow('Прибытие:', QLabel(details['arrival_time'].strftime('%d.%m.%Y %H:%M')))

        info_layout.addItem(QSpacerItem(20, 10))

        # Место
        info_layout.addRow('<b>МЕСТО:</b>', QLabel(''))
        info_layout.addRow('Вагон:', QLabel(str(details['carriage_number'])))
        info_layout.addRow('Место:', QLabel(str(details['seat_number'])))
        info_layout.addRow('Тип места:', QLabel(details['seat_type']))

        info_layout.addItem(QSpacerItem(20, 10))

        # Информация о бронировании
        info_layout.addRow('<b>ИНФОРМАЦИЯ О БРОНИРОВАНИИ:</b>', QLabel(''))

        status = details['status']
        confirmed = details['confirmed_by_admin']

        if confirmed:
            status_text = '✅ Подтверждено администратором'
        elif status == 'оплачен':
            status_text = '💰 Оплачено'
        elif status == 'забронирован':
            status_text = '⏳ Забронировано'
        else:
            status_text = '❌ Отменено'

        info_layout.addRow('Статус:', QLabel(status_text))
        info_layout.addRow('Создано пользователем:', QLabel(details['created_by_user']))
        info_layout.addRow('Дата бронирования:', QLabel(details['booking_date'].strftime('%d.%m.%Y %H:%M')))
        info_layout.addRow('Стоимость:', QLabel(f"{details['final_price']:.2f} ₽"))

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # Кнопки
        buttons_layout = QHBoxLayout()

        if not confirmed and status not in ['отменено', 'canceled', 'cancelled']:
            confirm_btn = QPushButton('✅ Подтвердить бронирование')
            confirm_btn.setMinimumHeight(40)
            confirm_btn.setStyleSheet(f'''
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
            confirm_btn.clicked.connect(lambda: self.confirm_and_close(details['booking_id'], dialog))
            buttons_layout.addWidget(confirm_btn)

        if status in ['забронирован', 'booked', 'reserved', 'оплачен', 'paid']:
            cancel_btn = QPushButton('❌ Отменить бронирование')
            cancel_btn.setMinimumHeight(40)
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
            cancel_btn.clicked.connect(lambda: self.cancel_and_close(details['booking_id'], dialog))
            buttons_layout.addWidget(cancel_btn)

        close_btn = QPushButton('Закрыть')
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet(f'''
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
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)

        close_btn = QPushButton('Закрыть')
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet(f'''
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
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def confirm_and_close(self, booking_id, dialog):
        """Подтвердить бронирование и закрыть окно"""
        self.confirm_booking(booking_id)
        dialog.accept()

    def cancel_and_close(self, booking_id, dialog):
        """Отменить бронирование и закрыть окно"""
        self.cancel_booking(booking_id)
        dialog.accept()

    def cancel_booking(self, booking_id):
        """Отмена бронирования администратором"""
        reply = QMessageBox.question(self, 'Отмена бронирования',
                                     f'Отменить бронирование №{booking_id}?',
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db.connect():
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                return

            if self.db.cancel_booking(booking_id):
                QMessageBox.information(self, 'Успех', 'Бронирование успешно отменено')
                self.load_all_bookings()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось отменить бронирование')

            self.db.disconnect()

    def change_user_role(self, new_role):
        """Изменение роли пользователя"""
        combo = self.sender()
        user_id = combo.property('user_id')

        reply = QMessageBox.question(self, 'Изменение роли',
                                     f'Изменить роль пользователя на "{new_role}"?',
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if not self.db.connect():
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                return

            if self.db.update_user_role(user_id, new_role):
                QMessageBox.information(self, 'Успех', 'Роль пользователя успешно изменена')
                self.load_all_users()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось изменить роль пользователя')

            self.db.disconnect()