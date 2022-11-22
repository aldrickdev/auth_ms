# standard imports
from typing import Optional
from datetime import datetime, timedelta

# third party imports
import fastapi
from jose import JWTError, jwt
from passlib.context import CryptContext

# user imports
import models
import exceptions
from utils import res_req_models

# context used for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tells your endpoints where to go to get a token if a valid token wasn't already
# provided by the client
oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="/api/v1/user/token/")


async def hash_password(password: str) -> str:
    """Returns the hashed password"""

    # hashes the password
    return pwd_context.hash(password)


async def validate_password(user: models.User, password: str) -> bool:
    """Returns True if the password matches the password in the database"""

    if not pwd_context.verify(password, user.hashed_password):
        return False

    return True


async def create_token(data: str, expires_in: int, secret: str, algorithm: str) -> str:
    """Returns a JWT"""

    # create the data to be encoded
    try:
        access_token_expires = timedelta(minutes=int(expires_in))

    except ValueError:
        raise ValueError("Time to expire not integer")

    data_to_encode = {
        "sub": data,
        "exp": datetime.utcnow() + access_token_expires,
    }

    # create the access token
    try:
        return jwt.encode(data_to_encode, secret, algorithm=algorithm)

    except JWTError:
        raise JWTError("Error Creating a JWT")


async def get_data_from_jwt(
    token: res_req_models.TokenData, secret: str, algorithm: str
) -> Optional[str]:
    """Return the username of the user in the token"""

    try:
        # decode the JWT
        payload = jwt.decode(token, secret, algorithms=algorithm)

    except jwt.JWTError:
        raise JWTError("Something went wrong when decoding the token")

    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("The signature has expired")

    except jwt.JWTClaimsError:
        raise jwt.JWTClaimsError("Claim was invalid")

    # return the username, if it doesn't exist return None
    data: str = payload.get("sub")

    if data is None:
        return None

    return data


async def validate_username(username: str) -> None:
    """Determines if the provided username is valid"""

    if not username.isalnum():
        raise exceptions.InvalidUsernameError("Whitespaces or Symbols Found in the Username")
