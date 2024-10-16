"""User model file."""
import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """User model."""

    user_id: Mapped[int] = mapped_column(
        sa.BigInteger, unique=True, nullable=False
    )
    """ Telegram user id """
    user_name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    age: Mapped[int] = mapped_column(
        sa.SmallInteger, unique=False, nullable=True
    )
    gender: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    country: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )

class Driver(Base):
    """Driver model."""
    
    user_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True, nullable=False)  # ID пользователя в Telegram
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)  # Имя водителя
    car_model: Mapped[str] = mapped_column(sa.Text, nullable=False)  # Модель автомобиля
    car_license_plate: Mapped[str] = mapped_column(sa.Text, nullable=False)  # Номерной знак автомобиля
    phone_number: Mapped[str] = mapped_column(sa.Text, nullable=False)  # Телефон водителя
    rating: Mapped[float] = mapped_column(sa.Float, default=5.0)  # Рейтинг водителя
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)  # Активный статус
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

class Passenger(Base):
    """Passenger model."""
    
    user_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True, nullable=False)  # ID пользователя в Telegram
    name: Mapped[str] = mapped_column(sa.Text, nullable=True)  # Имя пассажира
    phone_number: Mapped[str] = mapped_column(sa.Text, nullable=True)  # Телефон пассажира
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())