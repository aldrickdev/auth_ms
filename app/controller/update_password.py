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
async def update_password(
    password_obj: utils.UserUpdatePassword,
    token: str = fastapi.Depends(utils.oauth2_scheme),
) -> utils.UserDetails:
    """Endpoint used to update a users password"""

    # get variables for checking the token: if env vars don't exist, raise exception ===
    secret = env_vars.SECRET_KEY
    algorithm = env_vars.ALGORITHM
    # ===

    # get the username from JWT ===
    try:
        email = await utils.get_data_from_jwt(token, secret, algorithm)

    except (jose.JWTError, jose.jwt.ExpiredSignatureError, jose.jwt.JWTClaimsError) as err:
        raise exceptions.create_http_jwterror(err)
    # ===

    # get user from email: if no user found, raise exception ===
    user = await queries.get_user_by_email(email)

    if user is None:
        raise exceptions.HTTPUserWasNotFound

    # hash the password the user has provided
    hashed_password = await utils.hash_password(password_obj.password)

    # update the hashed_password field to true then return the updated user ===
    await user.update({"$set": {"hashed_password": hashed_password}})
    return utils.UserDetails(**user.dict())
    # ===
