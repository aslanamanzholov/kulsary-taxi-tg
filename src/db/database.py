"""Database class with all-in-one features."""

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from src.configuration import conf

from src.db.repositories import UserRepo, DriverRepo, DriverFeedbackRepo, TaxiRideRepo


def create_async_engine(url: URL | str) -> AsyncEngine:
    """Create async engine with given URL.

    :param url: URL to connect
    :return: AsyncEngine
    """
    return _create_async_engine(url=url, echo=conf.debug, pool_pre_ping=True)


class Database:
    """Database class.

    is the highest abstraction level of database and
    can be used in the handlers or any others bot-side functions.
    """

    user: UserRepo
    """ User repository """
    driver: DriverRepo
    """ Driver repository """
    taxi_ride: TaxiRideRepo
    """ Taxi ride repository """

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        user: UserRepo = None,
        driver: DriverRepo = None,
        taxi_ride: TaxiRideRepo = None,
        feedback: DriverFeedbackRepo = None,
    ):
        """Initialize Database class.

        :param session: AsyncSession to use
        :param user: (Optional) User repository
        :param driver: (Optional) Driver repository
        :param taxi_ride: (Optional) Taxi ride repository
        :param feedback: (Optional) Feedback repository
        """
        self.session = session
        self.user = user or UserRepo(session=session)
        self.driver = driver or DriverRepo(session=session)
        self.taxi_ride = taxi_ride or TaxiRideRepo(session=session)
        self.feedback = feedback or DriverFeedbackRepo(session=session)
