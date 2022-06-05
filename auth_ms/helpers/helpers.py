from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from auth_ms.models import User, UserInDB
from auth_ms.database import fake_users_db

SECRET_KEY = "eea1262491e6fe8111d93cd7a8fc761516b16531bf4e0b92e82b1f7e9c74fe18"
ALGORITHM = "HS256"

# This is what it used to tell FastAPI that a route is protected and will need
# the user to provide a token. The parameter tokenUrl tells the
# OAuthPasswordBearer that to obtain a token, the user will need to use the
# endpoint token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, sk, algo, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, sk, algorithm=algo)

    return encode_jwt


def fake_hash_password(password: str) -> str:
    """Adds to the password to act like a hash.

    Args:
        password (str): The password the user has entered.

    Returns:
        str: The hashed password.
    """
    return "fakehashed" + password


def fake_decode_token(token: str) -> User:
    """Takes the token, decodes it and returns the user information

    Args:
        token (str): The token sued to find the user

    Returns:
        User: The user that the token points too
    """
    user = get_user(fake_users_db, token)

    return user


def get_user(db: dict[str, dict[str, str | bool]], username: str) -> None | UserInDB:
    """Looks in the database for the user with the provided username.

    Args:
        db (dict[str, dict[str, str  |  bool]]): The database.
        username (str): The username we will be searching for.

    Returns:
        UserInDB or None: The user object if a user exist.
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

    return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Returns the current user from the token provided

    Args:
        token (str, optional): This is the token that the oauth2_scheme returns
        if it is provided in the request

    Raises:
        HTTPException: Raises a 401 error if we aren't able to get a user after
        decoding the token.

    Returns:
        User: The user instance if it is found when decoding the token
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user

    # user = fake_decode_token(token)

    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid Authentication Credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    # return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Checks to see if the current user is active

    Args:
        current_user (User, optional): Dependency that will get the current user

    Raises:
        HTTPException: Raises a 400 error if the user is disabled

    Returns:
        User: The active user
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")

    return current_user
