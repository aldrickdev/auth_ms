# standard imports
from datetime import datetime
from typing import Optional

# third party imports

# user imports
import models


async def create_user_record(username: str, email: str, hashed_password: str) -> models.User:
    """create a new user"""

    current_ts = datetime.now().timestamp()
    instance = models.User(
        username=username, email=email, hashed_password=hashed_password, created_ts=current_ts
    )

    await instance.insert()


async def get_user_from_username(username: str) -> Optional[models.User]:
    """returns a user if one is found, otherwise return None"""

    return await models.User.find_one(models.User.username == username)


async def get_user_by_email(email: str) -> models.User | None:
    """Returns a user if one is found when seaching using email, otherwise return None"""

    return await models.User.find_one(models.User.email == email)
