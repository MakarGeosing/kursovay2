from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Модель пользователя"""
    id: int
    username: str
    full_name: str
    role: str  # admin, user

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_user(self) -> bool:
        return self.role == 'user'


@dataclass
class Passenger:
    """Модель пассажира"""
    id: Optional[int] = None
    full_name: str = ""
    document_number: str = ""
    phone: str = ""


@dataclass
class Train:
    """Модель поезда"""
    id: int
    number: str
    name: str
    train_type: str


@dataclass
class Route:
    """Модель маршрута"""
    id: int
    train_id: int
    departure_station: str
    arrival_station: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    available_seats: int = 0


@dataclass
class Seat:
    """Модель места"""
    id: int
    carriage_number: int
    seat_number: int
    seat_type: str
    status: str  # свободно, забронировано, продано


@dataclass
class Booking:
    """Модель бронирования"""
    id: Optional[int] = None
    passenger_id: int = 0
    seat_id: int = 0
    route_id: int = 0
    status: str = "booked"  # забронирован, оплачен, отменен, подтвержден
    booking_date: Optional[datetime] = None
    price: float = 0.0