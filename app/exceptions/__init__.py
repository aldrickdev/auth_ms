import fastapi


class InvalidCredentialsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidUsernameError(Exception):
    pass


class DuplicateUserError(Exception):
    pass


class EmailInUseError(Exception):
    pass


# Common HTTPExceptions
MissingEnvironmentVariables = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Missing Environment Variables",
)

HTTPInvalidCredentials = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
    detail="Invalid Credentials",
)

HTTPUserWasNotFound = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
    detail="User was Not Found",
)

HTTPInvalidDataProvided = fastapi.HTTPException(
    status_code=fastapi.status.HTTP_400_BAD_REQUEST,
    detail="Provided Data was Not Valid",
)


def create_http_jwterror(error: str) -> None:
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail=f"{error}",
    )
