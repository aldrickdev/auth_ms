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


@router.put(
    path="/",
    status_code=fastapi.status.HTTP_202_ACCEPTED,
    response_model=utils.UserDetails,
)
async def disable_user(
    token: str = fastapi.Depends(utils.oauth2_scheme),
) -> utils.UserDetails:
    """Endpoint used to update a users information"""

    # get variables for creating the token: if env vars don't exist, raise exception ===
    secret = env_vars.SECRET_KEY
    algorithm = env_vars.ALGORITHM
    # ===

    # get the email from JWT ===
    try:
        email = await utils.get_data_from_jwt(token, secret, algorithm)

    except (jose.JWTError, jose.jwt.ExpiredSignatureError, jose.jwt.JWTClaimsError) as err:
        raise exceptions.create_http_jwterror(err)
    # ===

    # get user from email: if no user found, raise exception ===
    user = await queries.get_user_by_email(email)

    if user is None:
        raise exceptions.HTTPUserWasNotFound
    # ===

    # update the disabled field to true then return the updated user ===
    await user.update({"$set": {"disabled": True}})

    return utils.UserDetails(**user.dict())
    # ===
