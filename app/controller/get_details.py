# std
# 3p
import fastapi
import jose

# user
import env_vars
import exceptions
import queries
import utils

router = fastapi.APIRouter()


@router.get(
    path="/",
    status_code=fastapi.status.HTTP_200_OK,
    response_model=utils.UserDetails,
)
async def get_user_details(
    token: str = fastapi.Depends(utils.oauth2_scheme),
) -> utils.UserDetails:
    """Endpoint to get user information"""

    # get variables for creating the token: if doesn't exist, raise exception ===
    secret = env_vars.SECRET_KEY
    algorithm = env_vars.ALGORITHM
    # ===

    # get the email from JWT ===
    try:
        email = await utils.get_data_from_jwt(token, secret, algorithm)

    except (jose.JWTError, jose.jwt.ExpiredSignatureError, jose.jwt.JWTClaimsError) as err:
        raise exceptions.create_http_jwterror(err)
    # ===

    # get user from username: if the user is not found, raise exception ===
    user = await queries.get_user_by_email(email)

    if user is None:
        raise exceptions.HTTPUserWasNotFound

    return utils.UserDetails(**user.dict())
    # ===
