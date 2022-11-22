# standard imports
from typing import Literal

# third party imports
import pydantic

# user imports
import beanie


class User(beanie.Document):
    """The model the represents the User in the database"""

    username: beanie.Indexed(str, unique=True) = pydantic.Field(min_length=8, max_length=30)
    email: beanie.Indexed(pydantic.EmailStr, unique=True)
    disabled: bool | None = False
    role: Literal["standard", "admin"] | None = "standard"
    hashed_password: str
    created_ts: float

    class Settings:
        name = "Users"
