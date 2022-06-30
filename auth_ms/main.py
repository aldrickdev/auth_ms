from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from auth_ms.database import create_db_and_tables, engine, add_user
from auth_ms.env import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from auth_ms.helpers import (
    get_user_from_jwt,
    authenticate_user,
    oauth2_scheme,
    create_access_token,
    get_session,
    get_password_hash,
)
from auth_ms.models import Token, UserCreate, UserRead, User


# Create the FastAPI app instance
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/api/v1/create_user/", response_model=UserRead)
def create_user(
    provided_user: UserCreate, session: Session = Depends(get_session)
) -> UserRead:
    """Endpoint to create a User

    Args:
        provided_user (UserCreate): Model of what the client posts
        session (Session, optional): Database session

    Raises:
        HTTPException: Raises a 409 Conflict error if the user attempting to be created
        already exist

    Returns:
        UserRead: Returns a UserRead Object
            {
                "username": "<USERNAME>",
                "full_name": "<FULL_NAME>",
                "email": "<EMAIL>",
                "disabled": <BOOL>
            }
    """
    # New User
    new_user = User.from_orm(provided_user)

    # Check if the user trying to be created already exist
    statement = select(User).where(User.username == provided_user.username)
    results = session.exec(statement)

    if results.first() is not None:
        print(f"Username already exist: {results}")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User Already Exist",
        )

    # User doesn't exist, create it
    new_user.hashed_password = get_password_hash(provided_user.password)
    new_user = add_user(session, new_user)
    return new_user


@app.get("/api/v1/user_details/", response_model=UserRead)
def user_details(
    session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> UserRead:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_user_from_jwt(token, session)

    if user is None:
        raise credentials_exception

    return user


# @app.get("/api/v1/users/me")
# async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
#     """Returns the user data.

#     Args:
#         current_user (User): The user returned by the get_current_active_user
#         dependency.

#     Returns:
#         User: The user.
#     """
#     return current_user


@app.post("/token", response_model=Token)
async def login(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """Endpoint used to create a token for the user

    Args:
        form_data (OAuth2PasswordRequestForm): Checks the form data.

    Raises:
        HTTPException: Exception raised if the user doesn't exist.

    Returns:
        Token: The token used for authentication.
    """

    # Try to authenticate the user using the username and password provided
    user = authenticate_user(session, form_data.username, form_data.password)

    # If the user doesn't exist, raise an exception
    if user is None:
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
