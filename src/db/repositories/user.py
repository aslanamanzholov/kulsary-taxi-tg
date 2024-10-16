from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from .abstract import Repository


class UserRepo(Repository[User]):
    """User repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        super().__init__(type_model=User, session=session)

    async def new(
            self,
            user_id: int,
            user_name: str | None = None,
            name: str | None = None,
            phone_number: str | None = None,
    ) -> None:
        """Insert a new user into the database."""
        await self.session.merge(
            User(
                user_id=user_id,
                user_name=user_name,
                name=name,
                phone_number=phone_number
            )
        )
        await self.session.commit()

    async def user_register_check(self, user_id: int):
        """Check if user is already registered."""
        return (await self.session.scalars(
            select(self.type_model).where(User.user_id == user_id).limit(1)
        )).one_or_none()

    async def get_user_by_id(self, user_id: int):
        """Get user by ID."""
        statement = select(self.type_model).where(User.user_id == user_id)
        return (await self.session.scalars(statement)).first()
