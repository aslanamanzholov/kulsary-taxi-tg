from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import TaxiRide, Driver
from .abstract import Repository


class TaxiRideRepo(Repository[TaxiRide]):
    """Taxi Ride repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize taxi ride repository."""
        super().__init__(type_model=TaxiRide, session=session)

    async def new(
            self,
            passenger_id: int,
            driver_id: int,
            start_location: str,
            end_location: str,
            price: float,
            status: str = "pending",
    ) -> None:
        """Insert a new taxi ride into the database."""
        await self.session.merge(
            TaxiRide(
                passenger_id=passenger_id,
                driver_id=driver_id,
                start_location=start_location,
                end_location=end_location,
                price=price,
                status=status,
            )
        )
        await self.session.commit()

    async def get_ride_by_id(self, ride_id: int):
        """Get taxi ride by ID."""
        statement = select(self.type_model).where(TaxiRide.ride_id == ride_id)
        return (await self.session.scalars(statement)).first()

    async def get_rides_by_passenger_id(self, passenger_id: int, limit: int = 10):
        """Get rides for a specific passenger."""
        statement = select(self.type_model).where(TaxiRide.passenger_id == passenger_id).limit(limit)
        return (await self.session.scalars(statement)).all()

    async def get_rides_by_driver_id(self, driver_id: int, limit: int = 10):
        """Get rides for a specific driver."""
        statement = select(self.type_model).where(TaxiRide.driver_id == driver_id).limit(limit)
        return (await self.session.scalars(statement)).all()

class DriverRepo(Repository[Driver]):
    """Driver repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize driver repository."""
        super().__init__(type_model=Driver, session=session)

    async def new(
            self,
            user_id: int,
            username: str | None = None,
            name: str | None = None,
            vehicle_info: str | None = None,
            price: str | None = None,
    ) -> None:
        """Insert a new driver into the database.

        :param user_id: Telegram user id
        :param username: Telegram username
        :param name: Name of Driver
        :param vehicle_info: Information about the vehicle
        :param price: Price of the ride
        """
        await self.session.merge(
            Driver(
                user_id=user_id,
                username=username,
                name=name,
                vehicle_info=vehicle_info,
                price=price
            )
        )
        await self.session.commit()

    async def get_driver_by_id(self, driver_id: int):
        """Get driver by id."""
        statement = select(self.type_model).where(self.type_model.id == int(driver_id))
        return (await self.session.scalars(statement)).first()

    async def get_all_drivers(self, limit: int = 15):
        """Get all drivers."""
        statement = select(self.type_model).limit(limit)
        return (await self.session.scalars(statement)).all()