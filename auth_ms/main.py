from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer

from auth_ms.helpers import fake_decode_token
from auth_ms.models.user import User

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
