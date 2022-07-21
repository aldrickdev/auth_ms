from typing import Optional

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    username: str
    full_name: str
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "bestUser",
                "full_name": "Aldrick Castro",
                "email": "aldrick@gmail.com",
                "password": "password12345678",
            }
        }


class UserRead(SQLModel):
    username: str
    full_name: str
    email: str
    role: str
    disabled: bool

    class Config:
        schema_extra = {
            "example": {
                "username": "bestUser",
                "full_name": "Aldrick Castro",
                "email": "aldrick@gmail.com",
                "role": "standard",
                "disabled": "false",
            }
        }


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    full_name: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str = Field(default=None)
    role: str = Field(default="standard")
    disabled: bool = Field(default=False)
