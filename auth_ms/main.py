from datetime import timedelta, datetime
import logging.config

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pythonjsonlogger import jsonlogger
from sqlmodel import Session, select

from auth_ms.database import (
    create_db_and_tables,
    add_user,
    disable_user,
)
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
from auth_ms.metadata import (
    title,
    description,
    version,
    contact,
    license_info,
    tags_metadata,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        log_record["datetime"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        if log_record["level"]:
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
        log_record["env"] = "test"


formatter = CustomJsonFormatter("%(datetime)s %(level)s %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Create the FastAPI app instance
app = FastAPI(
    title=title,
    description=description,
    version=version,
    contact=contact,
    license_info=license_info,
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
def on_startup():
    logger.info("This New Application is Starting...")
    create_db_and_tables()


@app.post(
    "/api/v1/user/create",
    tags=["Users"],
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
)
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

    logger.info("New User created", extra=vars(new_user))

    return new_user


@app.get(
    "/api/v1/user/details/",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Users"],
    response_model=UserRead,
)
def user_details(
    session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> UserRead:
    """Endpoint to pull logged in user's details

    Args:
        session (Session, optional): Database session. Defaults to Depends(get_session).
        token (str, optional): JWT. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: 401 Error because the user couldn't be authenticated

    Returns:
        UserRead: The UserRead Object
            {
                "username": "<USERNAME>",
                "full_name": "<FULL_NAME>",
                "email": "<EMAIL>",
                "role: "<ROLE>",
                "disabled": <BOOL>
            }
    """
    # Checks requesting details exists
    user = get_user_from_jwt(token, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.get(
    "/api/v1/user/disable/",
    status_code=status.HTTP_200_OK,
    tags=["Users"],
    response_model=UserRead,
)
def user_disable(
    session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> UserRead:
    """Endpoint used to disable a user

    Args:
        session (Session): The database session
        token (str): The token used to authenticate the user

    Raises:
        HTTPException: 401 Error because the user couldn't be authenticated

    Returns:
        UserRead: The UserRead Object
            {
                "username": "<USERNAME>",
                "full_name": "<FULL_NAME>",
                "email": "<EMAIL>",
                "role: "<ROLE>",
                "disabled": <BOOL>
            }
    """
    # Checks requesting details exists
    user = get_user_from_jwt(token, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return disable_user(session, user)


@app.post(
    "/token", status_code=status.HTTP_201_CREATED, tags=["Token"], response_model=Token
)
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
