from typing import Optional

from sqlmodel import create_engine, SQLModel, Session, select
from sqlmodel.sql.expression import Select, SelectOfScalar
from sqlalchemy.exc import OperationalError

from auth_ms.models import User

# Temp solution regarding cachling warnings
# Solution Link: https://github.com/tiangolo/sqlmodel/issues/189#issuecomment-1025190094
# Link to Warning Information: https://bit.ly/3xLAshl
SelectOfScalar.inherit_cache = True
Select.inherit_cache = True

# sqlite_file_name = "db.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

# engine = None
# postgresql+psycopg2://user:password@host:port/dbname
engine = create_engine("postgresql+psycopg2://postgres:password@postgres:5432/User")


def create_db_and_tables() -> None:
    """Used to setup the data and make sure that the database is up and running before
    the rest of the application runs
    """
    while True:

        try:
            SQLModel.metadata.create_all(engine)
            break

        except OperationalError:
            continue


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
