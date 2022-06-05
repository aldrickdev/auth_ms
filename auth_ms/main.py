import os
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel

from auth_ms.database import fake_users_db
from auth_ms.helpers import (
    fake_hash_password,
    get_current_active_user,
    oauth2_scheme,
    authenticate_user,
    create_access_token,
)
from auth_ms.models import User, UserInDB


load_dotenv(find_dotenv())
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Create the FastAPI app instance
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Using the oauth2_scheme as a dependency for this route, telling FastAPI that
# this route is protected
# The way that this works it that when a request hits /protected, the
# 0auth2_scheme dependency will look to see if the request has an Authorization
# header, it then checks if the value is Bearer plus a token and then return
# that token as a string to the function handling the request.
# If it doesn't see the Authrization header or the value doesn't have a Bearer
# token then it will response with a 401 status code
@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Returns the active user.

    Args:
        current_user (User, optional): The active user.

    Returns:
        User: the active user.
    """
    return current_user


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """This is the endpoint that users that need a token, will be directed too.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): This is a dependency that
        declares a form body with a username, password, an optional scope and an
        optional grant_type.

    Raises:
        HTTPException: Raises a 400 error if the user doesn't exist in the database or
        if the hashed password doesn't match the hashed pasword that was saved in the
        database.

    Returns:
        dict[str, str]: This will return a dictionary with the structure of:
        {
            "access_token": <username>,
            "token_type": "bearer"
        }
    """

    user = authenticate_user(fake_users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        sk=SECRET_KEY,
        algo=ALGORITHM,
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}

    # user_dict = fake_users_db.get(form_data.username)

    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # user = UserInDB(**user_dict)
    # hashed_password = fake_hash_password(form_data.password)

    # if hashed_password != user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # return {"access_token": user.username, "token_type": "bearer"}
