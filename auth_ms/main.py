from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth_ms.helpers import fake_decode_token
from auth_ms.models.user import User

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

# Create the FastAPI app instance
app = FastAPI()

# This is what it used to tell FastAPI that a route is protected and will need
# the user to provide a token. The parameter tokenUrl tells the
# OAuthPasswordBearer that to obtain a token, the user will need to use the
# endpoint token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Returns the current user from the token provided

    Args:
        token (str, optional): This is the token that the oauth2_scheme returns
        if it is provided in the request

    Returns:
        User: The user instance if it is found when decoding the token
    """
    # Get the user from the token
    user = fake_decode_token(token)

    return user


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
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str:str]:
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
        dict[str:str]: This will return a dictionary with the structure of
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

    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
