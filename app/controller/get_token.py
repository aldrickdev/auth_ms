# std
# 3p
import fastapi

# user
import env_vars
import exceptions
import queries
import utils


router = fastapi.APIRouter()


@router.post(
    path="/",
    status_code=fastapi.status.HTTP_200_OK,
    response_model=utils.Token,
)
async def get_token(
    form_data: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
) -> utils.Token:
    """Endpoint to get a token for a user"""

    # extract the username and password from the form ===
    email = form_data.username
    password = form_data.password
    # ===

    # get variables for creating the token: if doesn't exist, raise exception ===
    expires_in = env_vars.ACCESS_TOKEN_EXPIRE_MINUTES
    secret = env_vars.SECRET_KEY
    algorithm = env_vars.ALGORITHM
    # ===

    # check to see if the user exist in the database: if not raise exception ===
    user = await queries.get_user_by_email(email)
    if user is None:
        raise exceptions.HTTPInvalidCredentials

    if not await utils.validate_password(user, password):
        raise exceptions.HTTPInvalidCredentials
    # ===

    # create and return a token
    token = await utils.create_token(user.email, expires_in, secret, algorithm)

    return utils.Token(access_token=token, token_type="bearer")
    # ===
