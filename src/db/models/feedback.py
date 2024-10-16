import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DriverFeedback(Base):
    """Driver Feedback model."""

    passenger_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)  # ID пассажира
    driver_id: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)  # ID водителя
    rating: Mapped[int] = mapped_column(sa.SmallInteger, nullable=False, default=5)  # Рейтинг от 1 до 5
    comment: Mapped[str] = mapped_column(sa.Text, nullable=True)  # Текстовый отзыв
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())