from typing import Optional

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    username: str
    full_name: str
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    full_name: str
    email: str
    hashed_password: str
    disabled: bool


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    full_name: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str = Field(default=None)
    disabled: bool = Field(default=False)
