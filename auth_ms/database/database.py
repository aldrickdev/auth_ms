from typing import Optional

from sqlmodel import create_engine, SQLModel, Session, select

from auth_ms.models import User

sqlite_file_name = "db.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_user(db_session: Session, username: str) -> Optional[User]:
    """Get User info

    Args:
        db_session (Session): The database session
        username (str): The users username

    Returns:
        Optional[User]: Returns the user is its found
    """
    # Checks to see if the user in found in the database
    statement = select(User).where(User.username == username)
    results = db_session.exec(statement)

    return results.first()


def add_user(db_session: Session, user: User) -> User:
    """Adds a user

    Args:
        db_session (Session): _description_
        user (User): _description_

    Returns:
        User: _description_
    """
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def disable_user(db_session: Session, user: User) -> User:
    """Sets the disabled field to True

    Args:
        db_session (Session): The database session
        user (User): The user object

    Returns:
        User: The user that has been disabled
    """
    # Sets the disabled field to True
    user.disabled = True
    db_session.add(user)
    db_session.commit()

    return user
