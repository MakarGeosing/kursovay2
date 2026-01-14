# Конфигурация приложения
class Config:
    # Настройки базы данных
    DB_CONFIG = {
        'host': '90.188.238.92',
        'database': 'railway_db',
        'user': 'remote_user',
        'password': 'RemotePass123!',
        'port': 3306
    }

    # Настройки приложения
    APP_NAME = 'Система бронирования ЖД билетов'
    VERSION = '1.0'

    # Цветовая схема
    COLORS = {
        'primary': '#d32f2f',  # Красный РЖД
        'secondary': '#2196F3',  # Синий
        'success': '#4CAF50',  # Зеленый
        'warning': '#FF9800',  # Оранжевый
        'danger': '#f44336',  # Красный
        'dark': '#333333',  # Темный
        'light': '#f5f5f5'  # Светлый
    }

    # Размеры шрифтов
    FONT_SIZES = {
        'small': 12,
        'normal': 14,
        'large': 16,
        'xlarge': 18,
        'xxlarge': 24,
        'title': 28
    }