from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from auth_ms.database import fake_users_db
from auth_ms.helpers import fake_hash_password, get_current_active_user, oauth2_scheme
from auth_ms.models import User, UserInDB


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


@app.post("/token")
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
    user_dict = fake_users_db.get(form_data.username)

    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)

    if hashed_password != user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
