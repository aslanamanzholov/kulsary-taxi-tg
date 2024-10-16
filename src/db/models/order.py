"""Masseuse model file."""
import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TaxiRide(Base):
    """Taxi Ride model."""
    passenger_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)  # ID пассажира
    driver_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)  # ID водителя
    start_location: Mapped[str] = mapped_column(sa.Text, nullable=False)  # Место начала поездки
    end_location: Mapped[str] = mapped_column(sa.Text, nullable=False)  # Место окончания поездки
    price: Mapped[float] = mapped_column(sa.Float, nullable=False)  # Стоимость поездки
    status: Mapped[str] = mapped_column(sa.Text, default="pending")  # Статус поездки (pending, ongoing, completed)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())