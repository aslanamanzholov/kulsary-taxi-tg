from sqlalchemy.exc import PendingRollbackError, IntegrityError

from src.db.models import User


def register_user(message):
    username = message.from_user.username if message.from_user.username else None
    user = User(user_id=int(message.from_user.id), username=username, name=message.from_user.full_name,
                age=message.from_user.age, country=message.from_user.country)

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False
