from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
from database import Database
from config import Config
from ui.seat_selection_window import SeatSelectionWindow
from ui.passenger_info_window import PassengerInfoWindow
from ui.booking_confirmation_window import BookingConfirmationWindow


class RoutesPage(QWidget):
    """Страница просмотра рейсов"""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database()
        self.selected_route_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel('ДОСТУПНЫЕ РЕЙСЫ')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xxlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["dark"]};
            margin-bottom: 10px;
        ''')
        layout.addWidget(title)

        # Если пользователь - админ, показываем сообщение
        if self.user.is_admin():
            message = QLabel('Администраторы не могут выполнять бронирование билетов.\n'
                             'Используйте панель администратора для управления рейсами и бронированиями.')
            message.setStyleSheet(f'''
                font-size: {Config.FONT_SIZES["large"]}px;
                color: {Config.COLORS["primary"]};
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 8px;
                text-align: center;
            ''')
            message.setAlignment(Qt.AlignCenter)
            layout.addWidget(message)
            layout.addStretch()
            self.setLayout(layout)
            return

        # Фильтры
        filter_frame = QFrame()
        filter_frame.setStyleSheet('''
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
            }
        ''')

        filter_layout = QHBoxLayout()

        # Фильтр по станции отправления
        self.from_filter = QComboBox()
        self.from_filter.addItem('Все станции отправления')
        self.from_filter.setMinimumHeight(40)
        self.from_filter.setStyleSheet(f'''
            QComboBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
                min-width: 200px;
            }}
        ''')

        # Фильтр по станции назначения
        self.to_filter = QComboBox()
        self.to_filter.addItem('Все станции назначения')
        self.to_filter.setMinimumHeight(40)
        self.to_filter.setStyleSheet(f'''
            QComboBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
                min-width: 200px;
            }}
        ''')

        # Фильтр по дате
        self.date_filter = QComboBox()
        self.date_filter.addItems(['Все даты', 'Сегодня', 'Завтра', 'На этой неделе', 'На следующей неделе'])
        self.date_filter.setMinimumHeight(40)
        self.date_filter.setStyleSheet(f'''
            QComboBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}
        ''')

        # Кнопка обновления
        refresh_btn = QPushButton('🔄 Обновить список')
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["secondary"]};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        ''')
        refresh_btn.clicked.connect(self.load_routes)

        filter_layout.addWidget(QLabel('Откуда:'))
        filter_layout.addWidget(self.from_filter)
        filter_layout.addWidget(QLabel('Куда:'))
        filter_layout.addWidget(self.to_filter)
        filter_layout.addWidget(QLabel('Дата:'))
        filter_layout.addWidget(self.date_filter)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addStretch()

        filter_frame.setLayout(filter_layout)
        layout.addWidget(filter_frame)

        # Таблица рейсов
        layout.addSpacing(10)
        results_label = QLabel('СПИСОК РЕЙСОВ:')
        results_label.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["dark"]};
        ''')
        layout.addWidget(results_label)

        self.routes_table = QTableWidget()
        self.routes_table.setColumnCount(8)
        self.routes_table.setHorizontalHeaderLabels(
            ['Поезд', 'Откуда', 'Куда', 'Отправление', 'Прибытие', 'Цена', 'Свободных мест', 'Действия'])
        self.routes_table.horizontalHeader().setStretchLastSection(True)
        self.routes_table.doubleClicked.connect(self.on_route_double_clicked)
        self.routes_table.itemSelectionChanged.connect(self.selection_changed)

        # Настраиваем ширину колонок
        self.routes_table.setColumnWidth(0, 150)  # Поезд
        self.routes_table.setColumnWidth(1, 120)  # Откуда
        self.routes_table.setColumnWidth(2, 120)  # Куда
        self.routes_table.setColumnWidth(3, 140)  # Отправление
        self.routes_table.setColumnWidth(4, 140)  # Прибытие
        self.routes_table.setColumnWidth(5, 100)  # Цена
        self.routes_table.setColumnWidth(6, 120)  # Свободных мест

        layout.addWidget(self.routes_table)

        # Информация о выбранном рейсе
        self.selection_info = QLabel('Выберите рейс для бронирования')
        self.selection_info.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["normal"]}px;
            color: {Config.COLORS["dark"]};
            padding: 15px;
            background-color: #f0f8ff;
            border-radius: 8px;
            margin-top: 10px;
        ''')
        layout.addWidget(self.selection_info)

        # Кнопка бронирования
        self.book_btn = QPushButton('🚆 Забронировать выбранный рейс')
        self.book_btn.setMinimumHeight(50)
        self.book_btn.setStyleSheet(f'''
            QPushButton {{
                background-color: {Config.COLORS["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {Config.FONT_SIZES["large"]}px;
                font-weight: bold;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: #b71c1c;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        ''')
        self.book_btn.clicked.connect(self.book_selected_route)
        self.book_btn.setEnabled(False)
        layout.addWidget(self.book_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Загружаем данные при создании
        self.load_routes()
        self.load_filters()

    def load_filters(self):
        """Загрузка фильтров"""
        if not self.db.connect():
            return

        # Загружаем уникальные станции отправления
        query_departure = """
        SELECT DISTINCT departure_station 
        FROM routes 
        ORDER BY departure_station
        """
        self.db.cursor.execute(query_departure)
        departure_stations = self.db.cursor.fetchall()

        # Загружаем уникальные станции назначения
        query_arrival = """
        SELECT DISTINCT arrival_station 
        FROM routes 
        ORDER BY arrival_station
        """
        self.db.cursor.execute(query_arrival)
        arrival_stations = self.db.cursor.fetchall()

        self.db.disconnect()

        # Заполняем фильтры
        for station in departure_stations:
            self.from_filter.addItem(station['departure_station'])

        for station in arrival_stations:
            self.to_filter.addItem(station['arrival_station'])

    def load_routes(self):
        """Загрузка списка рейсов"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        # Строим запрос с учетом фильтров
        query = """
        SELECT 
            t.id as train_id,
            t.train_number,
            t.train_name,
            t.train_type,
            r.id as route_id,
            r.departure_station,
            r.arrival_station,
            r.departure_time,
            r.arrival_time,
            r.base_price,
            COUNT(s.id) as available_seats
        FROM trains t
        JOIN routes r ON t.id = r.train_id
        LEFT JOIN seats s ON s.route_id = r.id AND s.status = 'свободно'
        WHERE 1=1
        """

        params = []

        # Применяем фильтр по станции отправления
        from_station = self.from_filter.currentText()
        if from_station != 'Все станции отправления':
            query += " AND r.departure_station = %s"
            params.append(from_station)

        # Применяем фильтр по станции назначения
        to_station = self.to_filter.currentText()
        if to_station != 'Все станции назначения':
            query += " AND r.arrival_station = %s"
            params.append(to_station)

        # Применяем фильтр по дате
        date_filter = self.date_filter.currentText()
        today = datetime.now().date()

        if date_filter == 'Сегодня':
            query += " AND DATE(r.departure_time) = CURDATE()"
        elif date_filter == 'Завтра':
            query += " AND DATE(r.departure_time) = DATE_ADD(CURDATE(), INTERVAL 1 DAY)"
        elif date_filter == 'На этой неделе':
            query += " AND YEARWEEK(r.departure_time, 1) = YEARWEEK(CURDATE(), 1)"
        elif date_filter == 'На следующей неделе':
            query += " AND YEARWEEK(r.departure_time, 1) = YEARWEEK(DATE_ADD(CURDATE(), INTERVAL 7 DAY), 1)"

        query += """
        GROUP BY r.id, t.id, t.train_number, t.train_name, t.train_type,
                 r.departure_station, r.arrival_station, r.departure_time, 
                 r.arrival_time, r.base_price
        HAVING available_seats > 0
        ORDER BY r.departure_time
        """

        self.db.cursor.execute(query, params)
        routes = self.db.cursor.fetchall()
        self.db.disconnect()

        if not routes:
            self.routes_table.setRowCount(0)
            self.selection_info.setText('Нет доступных рейсов по выбранным критериям')
            self.book_btn.setEnabled(False)
            return

        # Заполняем таблицу
        self.routes_table.setRowCount(len(routes))

        for row, route in enumerate(routes):
            # Поезд
            train_text = f"{route['train_name']}\n({route['train_number']})"
            train_item = QTableWidgetItem(train_text)
            self.routes_table.setItem(row, 0, train_item)

            # Станции
            self.routes_table.setItem(row, 1, QTableWidgetItem(route['departure_station']))
            self.routes_table.setItem(row, 2, QTableWidgetItem(route['arrival_station']))

            # Время
            departure = route['departure_time'].strftime('%d.%m.%Y\n%H:%M')
            arrival = route['arrival_time'].strftime('%d.%m.%Y\n%H:%M')

            departure_item = QTableWidgetItem(departure)
            arrival_item = QTableWidgetItem(arrival)

            # Центрируем текст в ячейках с датами
            departure_item.setTextAlignment(Qt.AlignCenter)
            arrival_item.setTextAlignment(Qt.AlignCenter)

            self.routes_table.setItem(row, 3, departure_item)
            self.routes_table.setItem(row, 4, arrival_item)

            # Цена
            price_item = QTableWidgetItem(f"{route['base_price']:.2f} ₽")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.routes_table.setItem(row, 5, price_item)

            # Свободные места
            seats_item = QTableWidgetItem(str(route['available_seats']))
            seats_item.setTextAlignment(Qt.AlignCenter)

            # Цветовая индикация свободных мест
            if route['available_seats'] > 10:
                seats_item.setBackground(QColor(220, 255, 220))  # зеленый
            elif route['available_seats'] > 5:
                seats_item.setBackground(QColor(255, 255, 200))  # желтый
            elif route['available_seats'] > 0:
                seats_item.setBackground(QColor(255, 200, 200))  # красный

            self.routes_table.setItem(row, 6, seats_item)

            # Кнопка бронирования в таблице
            book_cell_btn = QPushButton('Забронировать')
            book_cell_btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: {Config.COLORS["primary"]};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: {Config.FONT_SIZES["small"]}px;
                }}
                QPushButton:hover {{
                    background-color: #b71c1c;
                }}
            ''')
            book_cell_btn.clicked.connect(lambda checked, r=row: self.book_route_by_row(r))
            self.routes_table.setCellWidget(row, 7, book_cell_btn)

            # Сохраняем route_id в userData
            self.routes_table.item(row, 0).setData(Qt.UserRole, route['route_id'])

        # Обновляем информацию
        self.selection_info.setText(f'Найдено {len(routes)} доступных рейсов. Выберите рейс для бронирования.')

    def on_route_double_clicked(self, index):
        """Обработка двойного клика по строке с рейсом"""
        row = index.row()
        if 0 <= row < self.routes_table.rowCount():
            self.book_route_by_row(row)

    def selection_changed(self):
        """Обработка изменения выбора в таблице"""
        current_row = self.routes_table.currentRow()
        has_selection = current_row >= 0

        if has_selection:
            # Получаем информацию о выбранном рейсе
            departure = self.routes_table.item(current_row, 1).text()
            arrival = self.routes_table.item(current_row, 2).text()
            train = self.routes_table.item(current_row, 0).text().split('\n')[0]
            departure_time = self.routes_table.item(current_row, 3).text().replace('\n', ' ')
            price = self.routes_table.item(current_row, 5).text()
            seats = self.routes_table.item(current_row, 6).text()

            self.selection_info.setText(
                f'<b>Выбран рейс:</b> {departure} → {arrival}<br>'
                f'<b>Поезд:</b> {train}<br>'
                f'<b>Отправление:</b> {departure_time}<br>'
                f'<b>Цена:</b> {price} | <b>Свободных мест:</b> {seats}'
            )
        else:
            self.selection_info.setText('Выберите рейс для бронирования')

        self.book_btn.setEnabled(has_selection)

    def book_selected_route(self):
        """Бронирование выбранного рейса"""
        current_row = self.routes_table.currentRow()
        if current_row >= 0:
            self.book_route_by_row(current_row)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите рейс из таблицы')

    def book_route_by_row(self, row):
        """Бронирование рейса по указанной строке"""
        # Получаем route_id из userData
        route_id_item = self.routes_table.item(row, 0)
        if route_id_item:
            self.selected_route_id = route_id_item.data(Qt.UserRole)
            self.start_booking_process()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось получить данные о рейсе')

    def start_booking_process(self):
        """Начало процесса бронирования"""
        if not self.selected_route_id:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран рейс')
            return

        # 1. Выбор места
        seat_dialog = SeatSelectionWindow(self.selected_route_id, self.user)

        if seat_dialog.exec_() == QDialog.Accepted:
            seat_id = seat_dialog.get_selected_seat()

            if seat_id:
                # 2. Ввод данных пассажира
                passenger_dialog = PassengerInfoWindow(self)

                if passenger_dialog.exec_() == QDialog.Accepted:
                    passenger_data = passenger_dialog.get_passenger_data()

                    # 3. Подтверждение бронирования
                    confirm_dialog = BookingConfirmationWindow(
                        self.selected_route_id,
                        seat_id,
                        passenger_data,
                        self.user.id,
                        self
                    )

                    if confirm_dialog.exec_() == QDialog.Accepted:
                        # Обновляем список рейсов
                        self.load_routes()

                        # Показываем сообщение об успехе
                        QMessageBox.information(self, 'Успех',
                                                'Билет успешно забронирован!\n'
                                                'Вы можете посмотреть его в разделе "Мои бронирования"')