from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import Database
from config import Config


class BookingsPage(QWidget):
    """Страница бронирований"""

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
        title = QLabel('МОИ БРОНИРОВАНИЯ')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xxlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["dark"]};
            margin-bottom: 10px;
        ''')
        layout.addWidget(title)

        # Панель управления
        control_layout = QHBoxLayout()

        refresh_btn = QPushButton('🔄 Обновить список')
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
        refresh_btn.clicked.connect(self.load_bookings)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            ['Все бронирования', 'Забронированные', 'Оплаченные', 'Подтвержденные', 'Отмененные'])
        self.filter_combo.setMinimumHeight(40)
        self.filter_combo.setStyleSheet(f'''
            QComboBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}
        ''')
        self.filter_combo.currentTextChanged.connect(self.load_bookings)

        control_layout.addWidget(refresh_btn)
        control_layout.addWidget(QLabel('Фильтр:'))
        control_layout.addWidget(self.filter_combo)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Таблица бронирований
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(8)
        self.bookings_table.setHorizontalHeaderLabels(
            ['ID', 'Пассажир', 'Поезд', 'Маршрут', 'Дата', 'Статус', 'Цена', 'Подтверждено'])
        self.bookings_table.horizontalHeader().setStretchLastSection(True)
        self.bookings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bookings_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.bookings_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Устанавливаем контекстное меню
        self.bookings_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bookings_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.bookings_table)

        # Статистика
        self.stats_label = QLabel('')
        self.stats_label.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["normal"]}px;
            color: {Config.COLORS["dark"]};
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 6px;
        ''')
        layout.addWidget(self.stats_label)

        layout.addStretch()

        self.setLayout(layout)

        # Загружаем данные при создании
        self.load_bookings()

        # Создаем контекстное меню
        self.create_context_menu()

    def create_context_menu(self):
        """Создание контекстного меню"""
        self.context_menu = QMenu(self)

        self.view_action = self.context_menu.addAction('👁 Просмотреть детали')
        self.view_action.triggered.connect(self.view_booking_details)

        self.context_menu.addSeparator()

        self.cancel_action = self.context_menu.addAction('❌ Отменить бронирование')
        self.cancel_action.triggered.connect(self.cancel_selected_booking)

        self.pay_action = self.context_menu.addAction('💰 Оплатить бронирование')
        self.pay_action.triggered.connect(self.pay_selected_booking)

    def show_context_menu(self, position):
        """Показать контекстное меню"""
        index = self.bookings_table.indexAt(position)
        if index.isValid():
            # Проверяем статус выбранного бронирования
            row = index.row()
            status_item = self.bookings_table.item(row, 5)
            if status_item:
                status_text = status_item.text()

                # Включаем/отключаем действия в зависимости от статуса
                self.cancel_action.setEnabled('Забронировано' in status_text or 'Оплачено' in status_text)
                self.pay_action.setEnabled('Забронировано' in status_text)

                self.context_menu.exec_(self.bookings_table.viewport().mapToGlobal(position))

    def load_bookings(self):
        """Загрузка списка бронирований"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        # Получаем бронирования пользователя
        all_bookings = self.db.get_user_bookings(self.user.id)
        self.db.disconnect()

        if not all_bookings:
            self.bookings_table.setRowCount(0)
            self.stats_label.setText('Нет активных бронирований')
            return

        # Фильтруем бронирования
        filter_text = self.filter_combo.currentText()
        if filter_text == 'Забронированные':
            bookings = [b for b in all_bookings if b['status'] == 'забронирован']
        elif filter_text == 'Оплаченные':
            bookings = [b for b in all_bookings if b['status'] == 'оплачен']
        elif filter_text == 'Подтвержденные':
            bookings = [b for b in all_bookings if
                        b.get('confirmed_by_admin') == 1 or b.get('confirmed_by_admin') == True]
        elif filter_text == 'Отмененные':
            bookings = [b for b in all_bookings if b['status'] == 'отменено']
        else:
            bookings = all_bookings

        # Заполняем таблицу
        self.bookings_table.setRowCount(len(bookings))

        total_amount = 0
        status_counts = {'забронировано': 0, 'оплачено': 0, 'подтверждено': 0, 'отменено': 0}

        for row, booking in enumerate(bookings):
            self.bookings_table.setItem(row, 0, QTableWidgetItem(str(booking['booking_id'])))
            self.bookings_table.setItem(row, 1, QTableWidgetItem(booking['full_name']))
            self.bookings_table.setItem(row, 2, QTableWidgetItem(booking['train_name']))

            route = f"{booking['departure_station']} → {booking['arrival_station']}"
            self.bookings_table.setItem(row, 3, QTableWidgetItem(route))

            date = booking['booking_date'].strftime('%d.%m.%Y %H:%M')
            self.bookings_table.setItem(row, 4, QTableWidgetItem(date))

            # Определяем цвет и текст статуса
            status = booking['status']
            confirmed = booking.get('confirmed_by_admin', False)

            if confirmed:
                status_text = '✅ Подтверждено'
                status_counts['подтверждено'] += 1
                total_amount += booking['final_price']
            elif status == 'оплачен':
                status_text = '💰 Оплачено'
                status_counts['оплачено'] += 1
                total_amount += booking['final_price']
            elif status == 'забронирован':
                status_text = '⏳ Забронировано'
                status_counts['забронировано'] += 1
            elif status == 'подтвержден':
                status_text = '✅ Подтверждено'
                status_counts['подтверждено'] += 1
                total_amount += booking['final_price']
            else:
                status_text = '❌ Отменено'
                status_counts['отменено'] += 1

            status_item = QTableWidgetItem(status_text)

            # Устанавливаем цвет фона для статуса
            if 'Подтверждено' in status_text:
                status_item.setBackground(QColor(220, 255, 220))  # светло-зеленый
            elif 'Оплачено' in status_text:
                status_item.setBackground(QColor(255, 255, 200))  # светло-желтый
            elif 'Забронировано' in status_text:
                status_item.setBackground(QColor(255, 245, 200))  # светло-оранжевый
            else:
                status_item.setBackground(QColor(255, 220, 220))  # светло-красный

            self.bookings_table.setItem(row, 5, status_item)

            # Цена
            price_item = QTableWidgetItem(f"{booking['final_price']:.2f} ₽")
            self.bookings_table.setItem(row, 6, price_item)

            # Подтверждено
            confirmed_item = QTableWidgetItem('✅ Да' if confirmed else '❌ Нет')
            self.bookings_table.setItem(row, 7, confirmed_item)

        # Обновляем статистику
        stats_text = f'''
        Всего бронирований: {len(all_bookings)} | 
        Забронировано: {status_counts['забронировано']} | 
        Оплачено: {status_counts['оплачено']} | 
        Подтверждено: {status_counts['подтверждено']} |
        Отменено: {status_counts['отменено']} |
        Общая сумма: {total_amount:.2f} ₽
        '''
        self.stats_label.setText(stats_text)

    def view_booking_details(self):
        """Просмотр деталей бронирования"""
        current_row = self.bookings_table.currentRow()
        if current_row >= 0:
            booking_id = self.bookings_table.item(current_row, 0).text()

            if not self.db.connect():
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                return

            details = self.db.get_booking_details(int(booking_id))
            self.db.disconnect()

            if details:
                self.show_booking_details(details)

    def show_booking_details(self, details):
        """Показать детали бронирования"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Детали бронирования №{details["booking_id"]}')
        dialog.setFixedSize(500, 600)

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
        confirmed = details.get('confirmed_by_admin', False)

        if confirmed:
            status_text = '✅ Подтверждено администратором'
        elif status == 'оплачен':
            status_text = '💰 Оплачено (ожидает подтверждения)'
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

        # Кнопка закрытия
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
                opacity: 0.9;
            }}
        ''')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def cancel_selected_booking(self):
        """Отмена выбранного бронирования"""
        current_row = self.bookings_table.currentRow()
        if current_row >= 0:
            booking_id = self.bookings_table.item(current_row, 0).text()
            status_item = self.bookings_table.item(current_row, 5)

            if status_item and ('Подтверждено' in status_item.text()):
                QMessageBox.warning(self, 'Ошибка', 'Нельзя отменить подтвержденное бронирование')
                return

            reply = QMessageBox.question(self, 'Отмена бронирования',
                                         f'Вы уверены, что хотите отменить бронирование №{booking_id}?',
                                         QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                if not self.db.connect():
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                    return

                if self.db.cancel_booking(int(booking_id)):
                    QMessageBox.information(self, 'Успех', 'Бронирование успешно отменено')
                    self.load_bookings()
                else:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось отменить бронирование')

                self.db.disconnect()

    def pay_selected_booking(self):
        """Оплата выбранного бронирования"""
        current_row = self.bookings_table.currentRow()
        if current_row >= 0:
            booking_id = self.bookings_table.item(current_row, 0).text()
            price_item = self.bookings_table.item(current_row, 6)

            if price_item:
                price = price_item.text().replace(' ₽', '')

                reply = QMessageBox.question(self, 'Оплата бронирования',
                                             f'Оплатить бронирование №{booking_id} на сумму {price} ₽?',
                                             QMessageBox.Yes | QMessageBox.No)

                if reply == QMessageBox.Yes:
                    if not self.db.connect():
                        QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                        return

                    try:
                        # Обновляем статус бронирования на "оплачен"
                        query = "UPDATE bookings SET status = 'оплачен' WHERE id = %s"
                        self.db.cursor.execute(query, (booking_id,))
                        self.db.connection.commit()

                        QMessageBox.information(self, 'Успех',
                                                f'Бронирование №{booking_id} успешно оплачено!\n'
                                                f'Сумма: {price} ₽\n'
                                                f'Бронирование ожидает подтверждения администратором.')
                        self.load_bookings()

                    except Exception as e:
                        QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить оплату: {str(e)}')

                    finally:
                        self.db.disconnect()