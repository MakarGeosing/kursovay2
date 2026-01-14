import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Any  # Добавляем этот импорт в начале
from config import Config
from models import User


class Database:
    """Класс для работы с базой данных"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Подключение к базе данных"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_CONFIG['host'],
                database=Config.DB_CONFIG['database'],
                user=Config.DB_CONFIG['user'],
                password=Config.DB_CONFIG['password'],
                port=Config.DB_CONFIG['port']
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return True

        except Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Отключение от базы данных"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        try:
            query = """
            SELECT id, username, full_name, role 
            FROM users 
            WHERE username = %s AND password_hash = SHA2(%s, 256)
            """

            self.cursor.execute(query, (username, password))
            result = self.cursor.fetchone()

            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    full_name=result['full_name'],
                    role=result['role']
                )
            return None

        except Error as e:
            print(f"Ошибка аутентификации: {e}")
            return None

    def register_user(self, username: str, password: str, full_name: str) -> bool:
        """Регистрация нового пользователя"""
        try:
            query = """
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (%s, SHA2(%s, 256), %s, 'user')
            """

            self.cursor.execute(query, (username, password, full_name))
            self.connection.commit()
            return True

        except Error as e:
            print(f"Ошибка регистрации: {e}")
            return False

    def check_username_exists(self, username: str) -> bool:
        """Проверка существования username"""
        try:
            query = "SELECT 1 FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"Ошибка проверки username: {e}")
            return False

    # ========== ПОЕЗДА И МАРШРУТЫ ==========

    def get_all_trains(self) -> List[Dict]:
        """Получение списка всех поездов"""
        try:
            query = """
            SELECT id, train_number, train_name, train_type
            FROM trains
            ORDER BY train_number
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Ошибка получения поездов: {e}")
            return []

    def add_train(self, train_number: str, train_name: str, train_type: str) -> bool:
        """Добавление нового поезда"""
        try:
            query = """
            INSERT INTO trains (train_number, train_name, train_type)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (train_number, train_name, train_type))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Ошибка добавления поезда: {e}")
            return False

    def add_route(self, train_id: int, departure_station: str, arrival_station: str,
                  departure_time: str, arrival_time: str, base_price: float) -> bool:
        """Добавление нового маршрута"""
        try:
            query = """
            INSERT INTO routes (train_id, departure_station, arrival_station, 
                               departure_time, arrival_time, base_price)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (train_id, departure_station, arrival_station,
                                        departure_time, arrival_time, base_price))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Ошибка добавления маршрута: {e}")
            return False

    def add_seats_for_route(self, route_id: int, num_seats: int) -> bool:
        """Добавление мест для маршрута"""
        try:
            # Добавляем места
            seat_query = """
            INSERT INTO seats (carriage_number, seat_number, seat_type, status, route_id)
            VALUES (%s, %s, %s, 'свободно', %s)
            """

            seats_added = 0
            carriage_num = 1
            seat_in_carriage = 1

            for i in range(num_seats):
                # Определяем тип места
                if seat_in_carriage <= 2:
                    seat_type = 'Люкс'
                elif seat_in_carriage <= 6:
                    seat_type = 'Купе'
                else:
                    seat_type = 'Стандарт'

                self.cursor.execute(seat_query, (carriage_num, seat_in_carriage, seat_type, route_id))
                seats_added += 1
                seat_in_carriage += 1

                if seat_in_carriage > 10:  # 10 мест в вагоне
                    carriage_num += 1
                    seat_in_carriage = 1

            self.connection.commit()
            return seats_added > 0

        except Error as e:
            print(f"Ошибка добавления мест: {e}")
            return False

    def get_all_available_routes(self, filters=None) -> List[Dict]:
        """Получение всех доступных рейсов с фильтрами"""
        try:
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

            # Применяем фильтры если они есть
            if filters:
                if filters.get('departure_station'):
                    query += " AND r.departure_station = %s"
                    params.append(filters['departure_station'])

                if filters.get('arrival_station'):
                    query += " AND r.arrival_station = %s"
                    params.append(filters['arrival_station'])

                if filters.get('date_filter'):
                    if filters['date_filter'] == 'today':
                        query += " AND DATE(r.departure_time) = CURDATE()"
                    elif filters['date_filter'] == 'tomorrow':
                        query += " AND DATE(r.departure_time) = DATE_ADD(CURDATE(), INTERVAL 1 DAY)"
                    elif filters['date_filter'] == 'this_week':
                        query += " AND YEARWEEK(r.departure_time, 1) = YEARWEEK(CURDATE(), 1)"
                    elif filters['date_filter'] == 'next_week':
                        query += " AND YEARWEEK(r.departure_time, 1) = YEARWEEK(DATE_ADD(CURDATE(), INTERVAL 7 DAY), 1)"

            query += """
            GROUP BY r.id, t.id, t.train_number, t.train_name, t.train_type,
                     r.departure_station, r.arrival_station, r.departure_time, 
                     r.arrival_time, r.base_price
            HAVING available_seats > 0
            ORDER BY r.departure_time
            """

            self.cursor.execute(query, params)
            return self.cursor.fetchall()

        except Error as e:
            print(f"Ошибка получения рейсов: {e}")
            return []

    def search_trains(self, from_station: str, to_station: str, date: str) -> List[Dict]:
        """Поиск поездов по маршруту"""
        try:
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
            WHERE r.departure_station LIKE %s 
                AND r.arrival_station LIKE %s
                AND DATE(r.departure_time) = %s
            GROUP BY r.id, t.id, t.train_number, t.train_name, t.train_type,
                     r.departure_station, r.arrival_station, r.departure_time, 
                     r.arrival_time, r.base_price
            HAVING available_seats > 0
            ORDER BY r.departure_time
            """

            self.cursor.execute(query, (f"%{from_station}%", f"%{to_station}%", date))
            return self.cursor.fetchall()

        except Error as e:
            print(f"Ошибка поиска поездов: {e}")
            return []

    def get_available_seats(self, route_id: int) -> List[Dict]:
        """Получение свободных мест для рейса"""
        try:
            query = """
            SELECT 
                s.id as seat_id,
                s.seat_number,
                s.seat_type,
                s.carriage_number,
                s.status
            FROM seats s
            WHERE s.route_id = %s AND s.status = 'свободно'
            ORDER BY s.carriage_number, s.seat_number
            """

            self.cursor.execute(query, (route_id,))
            return self.cursor.fetchall()

        except Error as e:
            print(f"Ошибка получения мест: {e}")
            return []

    # ========== БРОНИРОВАНИЯ ==========

    def create_booking(self, passenger_data: Dict, seat_id: int, route_id: int, user_id: int) -> Optional[int]:
        """Создание бронирования"""
        try:
            # Начинаем транзакцию
            self.cursor.execute("START TRANSACTION")

            # 1. Создаем пассажира
            passenger_query = """
            INSERT INTO passengers (full_name, document_number, phone)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(passenger_query, (
                passenger_data['full_name'],
                passenger_data['document_number'],
                passenger_data['phone']
            ))
            passenger_id = self.cursor.lastrowid

            # 2. Получаем цену маршрута
            price_query = "SELECT base_price FROM routes WHERE id = %s"
            self.cursor.execute(price_query, (route_id,))
            price_result = self.cursor.fetchone()
            price = price_result['base_price'] if price_result else 0

            # 3. Создаем бронирование
            booking_query = """
            INSERT INTO bookings (passenger_id, seat_id, route_id, status, final_price, user_id, confirmed_by_admin)
            VALUES (%s, %s, %s, 'забронирован', %s, %s, FALSE)
            """
            self.cursor.execute(booking_query, (passenger_id, seat_id, route_id, price, user_id))
            booking_id = self.cursor.lastrowid

            # 4. Обновляем статус места
            seat_query = "UPDATE seats SET status = 'забронировано' WHERE id = %s"
            self.cursor.execute(seat_query, (seat_id,))

            # Фиксируем транзакцию
            self.connection.commit()
            return booking_id

        except Error as e:
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка создания бронирования: {e}")
            return None

    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Получение списка бронирований пользователя"""
        try:
            query = """
            SELECT 
                b.id as booking_id,
                b.status,
                b.booking_date,
                b.final_price,
                p.full_name,
                t.train_name,
                r.departure_station,
                r.arrival_station,
                s.seat_number,
                s.carriage_number,
                b.confirmed_by_admin
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.id
            JOIN routes r ON b.route_id = r.id
            JOIN trains t ON r.train_id = t.id
            JOIN seats s ON b.seat_id = s.id
            WHERE b.user_id = %s
            ORDER BY b.booking_date DESC
            LIMIT 100
            """

            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()

        except Error as e:
            print(f"Ошибка получения бронирований: {e}")
            return []

    def get_all_bookings(self) -> List[Dict]:
        """Получение всех бронирований (для админа)"""
        try:
            query = """
            SELECT 
                b.id as booking_id,
                b.status,
                b.booking_date,
                b.final_price,
                b.confirmed_by_admin,
                p.full_name,
                p.document_number,
                p.phone,
                t.train_name,
                t.train_number,
                r.departure_station,
                r.arrival_station,
                r.departure_time,
                r.arrival_time,
                s.seat_number,
                s.carriage_number,
                s.seat_type,
                u.username as created_by_user,
                u.full_name as user_full_name
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.id
            JOIN routes r ON b.route_id = r.id
            JOIN trains t ON r.train_id = t.id
            JOIN seats s ON b.seat_id = s.id
            JOIN users u ON b.user_id = u.id
            ORDER BY b.booking_date DESC
            LIMIT 200
            """

            self.cursor.execute(query)
            return self.cursor.fetchall()

        except Error as e:
            print(f"Ошибка получения всех бронирований: {e}")
            return []

    def get_booking_details(self, booking_id: int) -> Optional[Dict]:
        """Получение детальной информации о бронировании"""
        try:
            query = """
            SELECT 
                b.id as booking_id,
                b.status,
                b.booking_date,
                b.final_price,
                b.confirmed_by_admin,
                p.full_name,
                p.document_number,
                p.phone,
                t.train_name,
                t.train_number,
                r.departure_station,
                r.arrival_station,
                r.departure_time,
                r.arrival_time,
                s.seat_number,
                s.carriage_number,
                s.seat_type,
                u.username as created_by_user
            FROM bookings b
            JOIN passengers p ON b.passenger_id = p.id
            JOIN routes r ON b.route_id = r.id
            JOIN trains t ON r.train_id = t.id
            JOIN seats s ON b.seat_id = s.id
            JOIN users u ON b.user_id = u.id
            WHERE b.id = %s
            """

            self.cursor.execute(query, (booking_id,))
            return self.cursor.fetchone()

        except Error as e:
            print(f"Ошибка получения деталей бронирования: {e}")
            return None

    def cancel_booking(self, booking_id: int) -> bool:
        """Отмена бронирования"""
        try:
            # Начинаем транзакцию
            self.cursor.execute("START TRANSACTION")

            # 1. Получаем seat_id для освобождения места
            seat_query = "SELECT seat_id FROM bookings WHERE id = %s"
            self.cursor.execute(seat_query, (booking_id,))
            seat_result = self.cursor.fetchone()

            if seat_result:
                # 2. Обновляем статус бронирования
                booking_query = "UPDATE bookings SET status = 'отменено' WHERE id = %s"
                self.cursor.execute(booking_query, (booking_id,))

                # 3. Освобождаем место
                seat_query = "UPDATE seats SET status = 'свободно' WHERE id = %s"
                self.cursor.execute(seat_query, (seat_result['seat_id'],))

            self.connection.commit()
            return True

        except Error as e:
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка отмены бронирования: {e}")
            return False

    def confirm_booking(self, booking_id: int) -> bool:
        """Подтверждение бронирования администратором"""
        try:
            query = """
            UPDATE bookings 
            SET status = 'подтвержден', confirmed_by_admin = TRUE 
            WHERE id = %s AND status != 'отменено'  # Не подтверждаем отмененные
            """
            self.cursor.execute(query, (booking_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0

        except Error as e:
            print(f"Ошибка подтверждения бронирования: {e}")
            return False

    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Обновление статуса бронирования"""
        try:
            query = "UPDATE bookings SET status = %s WHERE id = %s"
            self.cursor.execute(query, (status, booking_id))
            self.connection.commit()
            return self.cursor.rowcount > 0

        except Error as e:
            print(f"Ошибка обновления статуса бронирования: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """Получение списка всех пользователей"""
        try:
            query = """
            SELECT id, username, full_name, role, created_at
            FROM users
            WHERE role != 'admin'  # Не показываем админов
            ORDER BY created_at DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Ошибка получения пользователей: {e}")
            return []

    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Обновление роли пользователя"""
        try:
            query = "UPDATE users SET role = %s WHERE id = %s"
            self.cursor.execute(query, (new_role, user_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Ошибка обновления роли пользователя: {e}")
            return False