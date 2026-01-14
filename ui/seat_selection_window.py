from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import Database
from config import Config


class SeatSelectionWindow(QDialog):
    """Окно выбора места"""

    def __init__(self, route_id, user):
        super().__init__()
        self.route_id = route_id
        self.user = user
        self.db = Database()
        self.selected_seat_id = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Выбор места')
        self.setFixedSize(900, 700)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel('ВЫБОР МЕСТА')
        title.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["xlarge"]}px;
            font-weight: bold;
            color: {Config.COLORS["primary"]};
        ''')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Информация о маршруте
        self.route_info_label = QLabel('')
        self.route_info_label.setStyleSheet(f'''
            font-size: {Config.FONT_SIZES["normal"]}px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 6px;
        ''')
        layout.addWidget(self.route_info_label)

        # Легенда
        legend_frame = QFrame()
        legend_frame.setStyleSheet('''
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        ''')

        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(15)

        legend_items = [
            ('свободно', Config.COLORS["success"]),
            ('люкс', Config.COLORS["primary"]),
            ('купе', Config.COLORS["secondary"]),
            ('выбрано', Config.COLORS["warning"])
        ]

        for text, color in legend_items:
            item_layout = QHBoxLayout()
            color_label = QLabel()
            color_label.setFixedSize(20, 20)
            color_label.setStyleSheet(f'background-color: {color}; border-radius: 4px;')
            text_label = QLabel(text)
            text_label.setStyleSheet(f'font-size: {Config.FONT_SIZES["small"]}px;')

            item_layout.addWidget(color_label)
            item_layout.addWidget(text_label)
            legend_layout.addLayout(item_layout)

        legend_layout.addStretch()
        legend_frame.setLayout(legend_layout)
        layout.addWidget(legend_frame)

        # Сетка мест
        self.seats_grid = QGridLayout()
        self.seats_grid.setSpacing(10)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.seats_grid)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.select_btn = QPushButton('Выбрать место')
        self.select_btn.setMinimumHeight(45)
        self.select_btn.setStyleSheet(f'''
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
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        ''')
        self.select_btn.clicked.connect(self.accept)
        self.select_btn.setEnabled(False)

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

        buttons_layout.addWidget(self.select_btn)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Загружаем данные
        self.load_route_info()
        self.load_seats()

    def load_route_info(self):
        """Загрузка информации о маршруте"""
        if not self.db.connect():
            return

        query = """
        SELECT 
            t.train_name,
            t.train_number,
            r.departure_station,
            r.arrival_station,
            r.departure_time,
            r.arrival_time,
            r.base_price
        FROM routes r
        JOIN trains t ON r.train_id = t.id
        WHERE r.id = %s
        """

        self.db.cursor.execute(query, (self.route_id,))
        route = self.db.cursor.fetchone()
        self.db.disconnect()

        if route:
            info_text = f'''
            <b>{route['train_name']} ({route['train_number']})</b><br>
            <b>Маршрут:</b> {route['departure_station']} → {route['arrival_station']}<br>
            <b>Отправление:</b> {route['departure_time'].strftime('%d.%m.%Y %H:%M')}<br>
            <b>Прибытие:</b> {route['arrival_time'].strftime('%d.%m.%Y %H:%M')}<br>
            <b>Цена:</b> {route['base_price']:.2f} ₽
            '''
            self.route_info_label.setText(info_text)

    def load_seats(self):
        """Загрузка доступных мест"""
        if not self.db.connect():
            QMessageBox.critical(self, 'Ошибка', 'Не удалось подключиться к базе данных')
            self.reject()
            return

        seats = self.db.get_available_seats(self.route_id)
        self.db.disconnect()

        if not seats:
            QMessageBox.information(self, 'Информация', 'Нет свободных мест на этот рейс')
            self.reject()
            return

        # Сортируем по вагонам
        carriages = {}
        for seat in seats:
            carriage_num = seat['carriage_number']
            if carriage_num not in carriages:
                carriages[carriage_num] = []
            carriages[carriage_num].append(seat)

        # Создаем виджеты мест
        row = 0
        for carriage_num in sorted(carriages.keys()):
            # Заголовок вагона
            carriage_label = QLabel(f'Вагон {carriage_num}')
            carriage_label.setStyleSheet(f'''
                font-size: {Config.FONT_SIZES["large"]}px;
                font-weight: bold;
                color: {Config.COLORS["primary"]};
                margin-top: 20px;
                padding: 5px;
                background-color: #f0f8ff;
                border-radius: 4px;
            ''')
            self.seats_grid.addWidget(carriage_label, row, 0, 1, 10)
            row += 1

            # Места в вагоне
            col = 0
            for seat in carriages[carriage_num]:
                seat_btn = QPushButton(str(seat['seat_number']))
                seat_btn.setFixedSize(50, 50)
                seat_btn.setProperty('seat_id', seat['seat_id'])
                seat_btn.setCursor(Qt.PointingHandCursor)

                # Цвет в зависимости от типа места
                seat_type = seat['seat_type'].lower() if seat['seat_type'] else 'standard'
                if 'люкс' in seat_type or 'lux' in seat_type:
                    color = Config.COLORS["primary"]
                elif 'купе' in seat_type:
                    color = Config.COLORS["secondary"]
                else:
                    color = Config.COLORS["success"]

                seat_btn.setStyleSheet(f'''
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: 2px solid {color};
                        border-radius: 8px;
                        font-size: {Config.FONT_SIZES["normal"]}px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: white;
                        color: {color};
                    }}
                    QPushButton:checked {{
                        background-color: white;
                        color: {color};
                        border: 3px solid {Config.COLORS["warning"]};
                    }}
                ''')

                seat_btn.setCheckable(True)
                seat_btn.toggled.connect(lambda checked, btn=seat_btn: self.seat_selected(checked, btn))

                self.seats_grid.addWidget(seat_btn, row, col)
                col += 1
                if col >= 10:  # 10 мест в ряд
                    col = 0
                    row += 1

            if col != 0:  # Если последний ряд не полный
                row += 1

    def seat_selected(self, checked, button):
        """Обработка выбора места"""
        if checked:
            # Снимаем выделение с других мест
            for i in range(self.seats_grid.count()):
                widget = self.seats_grid.itemAt(i).widget()
                if isinstance(widget, QPushButton) and widget != button:
                    widget.setChecked(False)

            self.selected_seat_id = button.property('seat_id')
            self.select_btn.setEnabled(True)
        else:
            if self.selected_seat_id == button.property('seat_id'):
                self.selected_seat_id = None
                self.select_btn.setEnabled(False)

    def get_selected_seat(self):
        """Получить выбранное место"""
        return self.selected_seat_id