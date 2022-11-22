# standard imports
from typing import Literal

# third party imports
import pydantic

# user imports


class UserDetails(pydantic.BaseModel):
    """The model that represents what basic user details are"""

    username: str = pydantic.Field(min_length=8, max_length=30)
    email: pydantic.EmailStr
    disabled: bool | None = False
    role: Literal["standard", "admin"] | None = "standard"


class UserCreateStepTwo(pydantic.BaseModel):
    """The model that represents what is expected from the client when completeing their signup"""

    username: str = pydantic.Field(min_length=8, max_length=30)
    password: str = pydantic.Field(min_length=8, max_length=36)

    class Config:
        schema_extra = {
            "example": {
                "username": "aldrickcastro",
                "password": "p@ssword",
            }
        }


class UserUpdate(pydantic.BaseModel):
    """The model that represents what is expected from the client when updating a users
    information"""

    email: pydantic.EmailStr | None = None
    role: Literal["standard", "admin"] | None = None


class UserUpdatePassword(pydantic.BaseModel):
    """Represents the requirements that a password must have when a user updates it"""

    password: str = pydantic.Field(min_length=8, max_length=36)


class UserForgotPasswordRequest(pydantic.BaseModel):
    """Represents the requirements that a forgot password request should have"""

    email: pydantic.EmailStr


class UserResetPasswordRequest(pydantic.BaseModel):
    """Represents the requirements that a reset password request should have"""

    password: str = pydantic.Field(min_length=8, max_length=36)


class Token(pydantic.BaseModel):
    """Model of a token"""

    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    """Model of a decoded token"""

    username: str | None = None
