from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from config import Config
from ui.routes_page import RoutesPage  # Изменено с routes_page.py
from ui.bookings_page import BookingsPage
from ui.admin_page import AdminPage


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, user):
        super().__init__()
        print(f"Создание MainWindow для пользователя: {user.username}, роль: {user.role}")
        self.user = user
        self.init_ui()

    def init_ui(self):
        # Настройки окна
        self.setWindowTitle(f'{Config.APP_NAME} - {self.user.full_name}')
        self.setGeometry(100, 50, 1200, 750)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # Шапка
        self.create_header(main_layout)

        # Навигация
        if not self.user.is_admin():
            self.create_navigation(main_layout)

        # Область контента
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Создаем страницы
        if not self.user.is_admin():
            # Для обычных пользователей
            self.routes_page = RoutesPage(self.user)  # Изменено с search_page
            self.bookings_page = BookingsPage(self.user)

            self.content_stack.addWidget(self.routes_page)
            self.content_stack.addWidget(self.bookings_page)

            # Показываем первую страницу
            self.content_stack.setCurrentWidget(self.routes_page)
            self.setWindowTitle(f'{Config.APP_NAME} - Доступные рейсы')
        else:
            # Для администратора
            self.admin_page = AdminPage(self.user)
            self.content_stack.addWidget(self.admin_page)

            # Показываем панель администратора
            self.content_stack.setCurrentWidget(self.admin_page)
            self.setWindowTitle(f'{Config.APP_NAME} - Панель администратора')

    def create_header(self, layout):
        """Создание шапки"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f'background-color: {Config.COLORS["primary"]};')

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Логотип и название
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(10)

        logo = QLabel('🚆')
        logo.setStyleSheet('font-size: 30px; color: white;')

        title = QLabel(Config.APP_NAME)
        title.setStyleSheet(f'''
            color: white;
            font-size: {Config.FONT_SIZES["xlarge"]}px;
            font-weight: bold;
        ''')

        logo_layout.addWidget(logo)
        logo_layout.addWidget(title)

        # Информация о пользователе
        user_layout = QHBoxLayout()
        user_layout.setSpacing(10)

        role_text = 'Администратор' if self.user.is_admin() else 'Пользователь'
        user_info = QLabel(f'{self.user.full_name}\n{role_text}')
        user_info.setStyleSheet(f'''
            color: white;
            font-size: {Config.FONT_SIZES["small"]}px;
            text-align: right;
        ''')

        logout_btn = QPushButton('Выйти')
        logout_btn.setFixedSize(80, 35)
        logout_btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        ''')
        logout_btn.clicked.connect(self.close)

        user_layout.addWidget(user_info)
        user_layout.addWidget(logout_btn)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        header_layout.addLayout(user_layout)

        header.setLayout(header_layout)
        layout.addWidget(header)

    def create_navigation(self, layout):
        """Создание навигации"""
        nav = QFrame()
        nav.setFixedHeight(50)
        nav.setStyleSheet(f'background-color: {Config.COLORS["light"]}; border-bottom: 1px solid #ddd;')

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(20, 0, 20, 0)
        nav_layout.setSpacing(10)

        # Кнопки навигации
        buttons = [
            ('🚆 Доступные рейсы', self.show_routes),  # Изменено название
            ('📋 Мои бронирования', self.show_bookings)
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(35)
            btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: {Config.COLORS["secondary"]};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: {Config.FONT_SIZES["normal"]}px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            ''')
            btn.clicked.connect(handler)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        nav.setLayout(nav_layout)
        layout.addWidget(nav)

    def show_routes(self):
        """Показать страницу рейсов"""
        self.content_stack.setCurrentWidget(self.routes_page)
        self.setWindowTitle(f'{Config.APP_NAME} - Доступные рейсы')

    def show_bookings(self):
        """Показать страницу бронирований"""
        self.bookings_page.load_bookings()
        self.content_stack.setCurrentWidget(self.bookings_page)
        self.setWindowTitle(f'{Config.APP_NAME} - Мои бронирования')