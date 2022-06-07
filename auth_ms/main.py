from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth_ms.database import fake_users_db
from auth_ms.helpers import (
    get_current_active_user,
    authenticate_user,
    create_access_token,
)
from auth_ms.models import User, Token
from auth_ms.env import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM


# Create the FastAPI app instance
app = FastAPI()


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """Returns the user data.

    Args:
        current_user (User): The user returned by the get_current_active_user
        dependency.

    Returns:
        User: The user.
    """
    return current_user


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Endpoint used to create a token for the user

    Args:
        form_data (OAuth2PasswordRequestForm): Checks the form data.

    Raises:
        HTTPException: Exception raised if the user doesn't exist.

    Returns:
        Token: The token used for authentication.
    """

    # Try to authenticate the user using the username and password provided
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)

    # If the user doesn't exist, raise an exception
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Creates a variable that has the time delta
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Creates the token
    access_token = create_access_token(
        data={"sub": user.username},
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        expires_delta=access_token_expires,
    )

    # Creates a Token instance and returns that
    return Token(access_token=access_token, token_type="bearer")
