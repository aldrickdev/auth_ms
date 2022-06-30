from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from auth_ms.models import User, TokenData
from auth_ms.database import engine
from auth_ms.env import SECRET_KEY, ALGORITHM


# This is what it used to tell FastAPI that a route is protected and will need
# the user to provide a token. The parameter tokenUrl tells the
# OAuthPasswordBearer that to obtain a token, the user will need to use the
# endpoint token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Used for hashing and verifying the password and hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Takes the user provided password and the hash from the database and validate if
    the provided password hashes to the same hash from the database.

    Args:
        plain_password (str): The password provided by the user.
        hashed_password (str): The hash from the database.

    Returns:
        bool: True if the provided password hashes to the expected hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes the provided password.

    Args:
        password (str): The password needing to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


# def authenticate_user(
#     fake_db: db_type, username: str, password: str
# ) -> UserInDB | bool:
#     """Authenticates a user.

#     Args:
#         fake_db (db_type): The database.
#         username (str): The user that needs to be authenticated.
#         password (str): The password the user provided.

#     Returns:
#         UserInDB | bool: Returns the user with its hashed password.
#     """

#     # Look to see if the user exists
#     user = get_user(fake_db, username)

#     # Check if we got a user back
#     if not user:
#         # Returns False if a user was not found
#         return False

#     # Check if the password is correct
#     if not verify_password(password, user.hashed_password):
#         # Returns False if the password isn't correct
#         return False

#     # Returns the user
#     return user


def create_access_token(
    data: dict, secret_key: str, algorithm: str, expires_delta: timedelta | None = None
):
    """Creates a token.

    Args:
        data (dict): The data to encode in the JWT.
        secret_key (str): The secret key used for encoding.
        algorithm (str): The algorithm being used for the encoding.
        expires_delta (timedelta | None, optional): The amount of time the token is
            valid. Defaults to None.

    Returns:
        str: The encoded token.
    """

    # Makes a copy of the data
    to_encode = data.copy()

    # If an expiration delta is given
    if expires_delta:
        # Set the expiry to the delta provided
        expire = datetime.utcnow() + expires_delta
    else:
        # Set the expiry to 15 minutes
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Add the dict that needs to be encoded to include the expiration time
    to_encode.update({"exp": expire})

    # Returns the JWT
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


# def get_user(db: db_type, username: str) -> UserInDB | None:
#     """Looks in the database for the user with the provided username.

#     Args:
#         db (dict[str, dict[str, str  |  bool]]): The database.
#         username (str): The username we will be searching for.

#     Returns:
#         UserInDB or None: The user object if a user exist.
#     """

#     # Checks to see if the user in found in the database
#     if username in db:
#         # Gets the user information and returns a user object
#         user_dict = db[username]
#         return UserInDB(**user_dict)

#     # User was not found so return None
#     return None


# def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
#     """Returns the current user from the token provided

#     Args:
#         token (str, optional): This is the token that the oauth2_scheme returns
#         if it is provided in the request

#     Raises:
#         HTTPException: Raises a 401 error if we aren't able to get a user after
#         decoding the token.

#     Returns:
#         User: The user instance if it is found when decoding the token
#     """

#     # Creates an exception to be used for not credentials that couldn't be validated
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         # Decode the JWT
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

#         # Pull out the username from the payload
#         username: str = payload.get("sub")

#         # Checks to see if the username was found in the payload
#         if username is None:
#             # Raises exception if the username was not in the payload
#             raise credentials_exception

#         # Creates a TokenData object with the username
#         token_data = TokenData(username=username)

#     # If there was an error decoding the JWT raise error
#     except JWTError:
#         raise credentials_exception

#     # Look for the user in the database by the username in the JWT payload
#     user = get_user(fake_users_db, username=token_data.username)

#     # If the user is not found raise exception
#     if user is None:
#         raise credentials_exception

#     # Returns the user
#     return user


# async def get_current_active_user(
#     current_user: User = Depends(get_current_user),
# ) -> User:
#     """Checks to see if the current user is active

#     Args:
#         current_user (User, optional): Dependency that will get the current user

#     Raises:
#         HTTPException: Raises a 400 error if the user is disabled

#     Returns:
#         User: The active user
#     """
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive User")

#     return current_user


def get_session():
    with Session(engine) as session:
        yield session
