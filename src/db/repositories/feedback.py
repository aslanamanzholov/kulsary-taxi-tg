from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import DriverFeedback
from src.db.repositories import Repository


class DriverFeedbackRepo(Repository[DriverFeedback]):
    """DriverFeedback repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize driver feedback repository."""
        super().__init__(type_model=DriverFeedback, session=session)

    async def new(
            self,
            feedback_user_id: int,
            driver_id: int,
            rate: int,
            feedback_username: str | None = None,
            text: str | None = None,
    ) -> None:
        """Insert a new feedback for the driver."""
        await self.session.merge(
            DriverFeedback(
                feedback_user_id=feedback_user_id,
                driver_id=driver_id,
                rate=rate,
                feedback_username=feedback_username,
                text=text
            )
        )
        await self.session.commit()

    async def get_feedback_by_driver_id(self, driver_id: int, offset: int = 0, limit: int = 1):
        """Get feedback by driver ID."""
        statement = select(self.type_model).where(DriverFeedback.driver_id == int(driver_id)).offset(offset).limit(limit)

        return (await self.session.scalars(statement)).first()

    async def get_feedback_count_by_driver_id(self, driver_id: int):
        """Get total feedback count for the driver."""
        statement = select(func.count()).where(DriverFeedback.driver_id == int(driver_id))
        return await self.session.scalar(statement)

    async def get_feedback_rate_list_by_driver_id(self, driver_id: int):
        """Get rating list for the driver."""
        statement = select(DriverFeedback.rate).where(DriverFeedback.driver_id == int(driver_id))
        return (await self.session.scalars(statement)).all()