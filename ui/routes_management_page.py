from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
from database import Database
from config import Config


class RoutesManagementPage(QWidget):
    """Страница управления рейсами (для админа)"""

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
        title = QLabel('УПРАВЛЕНИЕ РЕЙСАМИ')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xxlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["dark"]};
            margin-bottom: 10px;
        ''')
        layout.addWidget(title)

        # Вкладки
        self.tab_widget = QTabWidget()

        # Вкладка добавления рейса
        self.add_route_tab = self.create_add_route_tab()
        self.tab_widget.addTab(self.add_route_tab, '➕ Добавить рейс')

        # Вкладка управления поездами
        self.trains_tab = self.create_trains_tab()
        self.tab_widget.addTab(self.trains_tab, '🚆 Управление поездами')

        # Вкладка существующих рейсов
        self.routes_tab = self.create_routes_tab()
        self.tab_widget.addTab(self.routes_tab, '📋 Существующие рейсы')

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def create_add_route_tab(self):
        """Создание вкладки добавления рейса"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel('ДОБАВЛЕНИЕ НОВОГО РЕЙСА')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["large"]}px;
            font-weight: bold;
            color: {Config.COLORS["primary"]};
        ''')
        layout.addWidget(title)

        # Форма добавления рейса
        form_frame = QFrame()
        form_frame.setStyleSheet('''
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
        ''')

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Выбор поезда
        self.train_combo = QComboBox()
        self.train_combo.setMinimumHeight(40)
        self.train_combo.setStyleSheet(f'''
            QComboBox {{
                font-size: {Config.FONT_SIZES["normal"]}px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}
        ''')

        # Поле для нового поезда
        self.new_train_frame = QFrame()
        self.new_train_frame.setStyleSheet('''
            QFrame {
                background-color: #f0f8ff;
                border: 1px solid #b0d0ff;
                border-radius: 6px;
                padding: 15px;
                margin-top: 10px;
            }
        ''')
        new_train_layout = QGridLayout()
        new_train_layout.setSpacing(10)

        self.new_train_number = QLineEdit()
        self.new_train_number.setPlaceholderText('Номер поезда (например: 001А)')
        self.new_train_number.setMinimumHeight(40)

        self.new_train_name = QLineEdit()
        self.new_train_name.setPlaceholderText('Название поезда (например: Сапсан)')
        self.new_train_name.setMinimumHeight(40)

        self.new_train_type = QLineEdit()
        self.new_train_type.setPlaceholderText('Тип поезда (например: скоростной)')
        self.new_train_type.setMinimumHeight(40)

        new_train_layout.addWidget(QLabel('Номер поезда:'), 0, 0)
        new_train_layout.addWidget(self.new_train_number, 0, 1)
        new_train_layout.addWidget(QLabel('Название поезда:'), 1, 0)
        new_train_layout.addWidget(self.new_train_name, 1, 1)
        new_train_layout.addWidget(QLabel('Тип поезда:'), 2, 0)
        new_train_layout.addWidget(self.new_train_type, 2, 1)

        self.new_train_frame.setLayout(new_train_layout)
        self.new_train_frame.hide()

        # Поля маршрута
        self.departure_station = QLineEdit()
        self.departure_station.setPlaceholderText('Москва')
        self.departure_station.setMinimumHeight(40)

        self.arrival_station = QLineEdit()
        self.arrival_station.setPlaceholderText('Санкт-Петербург')
        self.arrival_station.setMinimumHeight(40)

        self.departure_time = QDateTimeEdit()
        current_time = QDateTime.currentDateTime()
        tomorrow = current_time.addDays(1)
        self.departure_time.setDateTime(tomorrow)
        self.departure_time.setDisplayFormat('dd.MM.yyyy HH:mm')
        self.departure_time.setCalendarPopup(True)
        self.departure_time.setMinimumHeight(40)

        self.arrival_time = QDateTimeEdit()
        tomorrow_plus_4h = tomorrow.addSecs(4 * 3600)
        self.arrival_time.setDateTime(tomorrow_plus_4h)
        self.arrival_time.setDisplayFormat('dd.MM.yyyy HH:mm')
        self.arrival_time.setCalendarPopup(True)
        self.arrival_time.setMinimumHeight(40)

        self.base_price = QDoubleSpinBox()
        self.base_price.setRange(100, 100000)
        self.base_price.setValue(2500.00)
        self.base_price.setPrefix('₽ ')
        self.base_price.setDecimals(2)
        self.base_price.setMinimumHeight(40)

        self.num_seats = QSpinBox()
        self.num_seats.setRange(10, 200)
        self.num_seats.setValue(50)
        self.num_seats.setMinimumHeight(40)

        form_layout.addRow('Поезд:', self.train_combo)
        form_layout.addRow('', self.new_train_frame)
        form_layout.addRow('Станция отправления:', self.departure_station)
        form_layout.addRow('Станция назначения:', self.arrival_station)
        form_layout.addRow('Время отправления:', self.departure_time)
        form_layout.addRow('Время прибытия:', self.arrival_time)
        form_layout.addRow('Базовая цена:', self.base_price)
        form_layout.addRow('Количество мест:', self.num_seats)

        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)

        # Кнопка добавления
        add_btn = QPushButton('✅ Добавить рейс')
        add_btn.setMinimumHeight(50)
        add_btn.setStyleSheet(f'''
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
        add_btn.clicked.connect(self.add_route)
        layout.addWidget(add_btn)

        widget.setLayout(layout)

        # Загружаем поезда
        self.load_trains()

        return widget

    def create_trains_tab(self):
        """Создание вкладки управления поездами"""
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
        refresh_btn.clicked.connect(self.load_trains_list)

        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Таблица поездов
        self.trains_table = QTableWidget()
        self.trains_table.setColumnCount(4)
        self.trains_table.setHorizontalHeaderLabels([
            'ID', 'Номер поезда', 'Название', 'Тип'
        ])
        self.trains_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.trains_table)

        widget.setLayout(layout)

        # Загружаем данные
        self.load_trains_list()

        return widget

    def create_routes_tab(self):
        """Создание вкладки существующих рейсов"""
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
        refresh_btn.clicked.connect(self.load_routes_list)

        control_layout.addWidget(refresh_btn)
        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Таблица рейсов
        self.routes_table = QTableWidget()
        self.routes_table.setColumnCount(8)
        self.routes_table.setHorizontalHeaderLabels([
            'ID', 'Поезд', 'Откуда', 'Куда', 'Отправление', 'Прибытие', 'Цена', 'Свободных мест'
        ])
        self.routes_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.routes_table)

        widget.setLayout(layout)

        # Загружаем данные
        self.load_routes_list()

        return widget

    def load_trains(self):
        """Загрузка поездов в комбобокс"""
        if not self.db.connect():
            return

        trains = self.db.get_all_trains()
        self.db.disconnect()

        self.train_combo.clear()
        if trains:
            for train in trains:
                self.train_combo.addItem(f"{train['train_name']} ({train['train_number']})", train['id'])

    def load_trains_list(self):
        """Загрузка списка поездов в таблицу"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        trains = self.db.get_all_trains()
        self.db.disconnect()

        if not trains:
            self.trains_table.setRowCount(0)
            return

        # Заполняем таблицу
        self.trains_table.setRowCount(len(trains))

        for row, train in enumerate(trains):
            self.trains_table.setItem(row, 0, QTableWidgetItem(str(train['id'])))
            self.trains_table.setItem(row, 1, QTableWidgetItem(train['train_number']))
            self.trains_table.setItem(row, 2, QTableWidgetItem(train['train_name']))
            self.trains_table.setItem(row, 3, QTableWidgetItem(train['train_type']))

    def load_routes_list(self):
        """Загрузка списка рейсов"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        # Получаем все рейсы с информацией о свободных местах
        query = """
        SELECT 
            r.id,
            t.train_name,
            t.train_number,
            r.departure_station,
            r.arrival_station,
            r.departure_time,
            r.arrival_time,
            r.base_price,
            COUNT(s.id) as free_seats
        FROM routes r
        JOIN trains t ON r.train_id = t.id
        LEFT JOIN seats s ON s.route_id = r.id AND s.status = 'свободно'
        GROUP BY r.id, t.train_name, t.train_number, r.departure_station, 
                 r.arrival_station, r.departure_time, r.arrival_time, r.base_price
        ORDER BY r.departure_time DESC
        LIMIT 100
        """

        self.db.cursor.execute(query)
        routes = self.db.cursor.fetchall()
        self.db.disconnect()

        if not routes:
            self.routes_table.setRowCount(0)
            return

        # Заполняем таблицу
        self.routes_table.setRowCount(len(routes))

        for row, route in enumerate(routes):
            self.routes_table.setItem(row, 0, QTableWidgetItem(str(route['id'])))
            self.routes_table.setItem(row, 1, QTableWidgetItem(f"{route['train_name']} ({route['train_number']})"))
            self.routes_table.setItem(row, 2, QTableWidgetItem(route['departure_station']))
            self.routes_table.setItem(row, 3, QTableWidgetItem(route['arrival_station']))

            departure = route['departure_time'].strftime('%d.%m.%Y %H:%M')
            arrival = route['arrival_time'].strftime('%d.%m.%Y %H:%M')

            self.routes_table.setItem(row, 4, QTableWidgetItem(departure))
            self.routes_table.setItem(row, 5, QTableWidgetItem(arrival))
            self.routes_table.setItem(row, 6, QTableWidgetItem(f"{route['base_price']:.2f} ₽"))

            # Свободные места с цветовой индикацией
            free_seats_item = QTableWidgetItem(str(route['free_seats']))
            if route['free_seats'] > 20:
                free_seats_item.setBackground(QColor(220, 255, 220))
            elif route['free_seats'] > 10:
                free_seats_item.setBackground(QColor(255, 255, 200))
            elif route['free_seats'] > 0:
                free_seats_item.setBackground(QColor(255, 200, 200))
            else:
                free_seats_item.setBackground(QColor(255, 150, 150))

            self.routes_table.setItem(row, 7, free_seats_item)

    def toggle_new_train_form(self):
        """Показать/скрыть форму добавления нового поезда"""
        if self.new_train_frame.isVisible():
            self.new_train_frame.hide()
        else:
            self.new_train_frame.show()

    def add_route(self):
        """Добавление нового рейса"""
        # Проверяем выбран ли поезд
        train_id = self.train_combo.currentData()

        if train_id == -1:
            # Добавляем новый поезд
            train_number = self.new_train_number.text().strip()
            train_name = self.new_train_name.text().strip()
            train_type = self.new_train_type.text().strip()

            if not train_number or not train_name or not train_type:
                QMessageBox.warning(self, 'Ошибка', 'Заполните все поля нового поезда')
                return

            if not self.db.connect():
                QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
                return

            if self.db.add_train(train_number, train_name, train_type):
                # Обновляем список поездов
                self.load_trains()
                # Выбираем только что добавленный поезд
                for i in range(self.train_combo.count() - 1):  # Исключаем последний элемент
                    if self.train_combo.itemText(i) == f"{train_name} ({train_number})":
                        self.train_combo.setCurrentIndex(i)
                        train_id = self.train_combo.currentData()
                        break
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удалось добавить поезд')
                self.db.disconnect()
                return

            self.db.disconnect()

        if not train_id or train_id == -1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите поезд')
            return

        # Получаем данные из формы
        departure_station = self.departure_station.text().strip()
        arrival_station = self.arrival_station.text().strip()
        departure_time = self.departure_time.dateTime().toString('yyyy-MM-dd HH:mm:00')
        arrival_time = self.arrival_time.dateTime().toString('yyyy-MM-dd HH:mm:00')
        base_price = self.base_price.value()
        num_seats = self.num_seats.value()

        # Валидация
        if not departure_station or not arrival_station:
            QMessageBox.warning(self, 'Ошибка', 'Заполните станции отправления и назначения')
            return

        if departure_station == arrival_station:
            QMessageBox.warning(self, 'Ошибка', 'Станция отправления и назначения не могут совпадать')
            return

        # Проверяем время (преобразуем строки в datetime для сравнения)
        dep_dt = QDateTime.fromString(departure_time, 'yyyy-MM-dd HH:mm:00')
        arr_dt = QDateTime.fromString(arrival_time, 'yyyy-MM-dd HH:mm:00')

        if arr_dt <= dep_dt:
            QMessageBox.warning(self, 'Ошибка', 'Время прибытия должно быть позже времени отправления')
            return

        if base_price <= 0:
            QMessageBox.warning(self, 'Ошибка', 'Цена должна быть больше 0')
            return

        if num_seats <= 0:
            QMessageBox.warning(self, 'Ошибка', 'Количество мест должно быть больше 0')
            return

        # Добавляем маршрут
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            return

        if self.db.add_route(train_id, departure_station, arrival_station,
                             departure_time, arrival_time, base_price):

            # Получаем ID добавленного маршрута
            query = "SELECT LAST_INSERT_ID() as route_id"
            self.db.cursor.execute(query)
            route_id = self.db.cursor.fetchone()['route_id']

            # Добавляем места
            if self.db.add_seats_for_route(route_id, num_seats):
                QMessageBox.information(self, 'Успех',
                                        f'Рейс успешно добавлен!\n'
                                        f'Добавлено мест: {num_seats}\n'
                                        f'ID маршрута: {route_id}')

                # Очищаем форму
                self.departure_station.clear()
                self.arrival_station.clear()
                self.departure_station.setFocus()

                # Обновляем таблицы
                self.load_routes_list()
                self.load_trains_list()
            else:
                QMessageBox.warning(self, 'Внимание',
                                    'Маршрут добавлен, но возникла ошибка при добавлении мест')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось добавить маршрут')

        self.db.disconnect()