# std
# 3p
import fastapi
import jose

# user
import env_vars
import exceptions
import utils
import queries

router = fastapi.APIRouter()


@router.put(
    path="/",
    status_code=fastapi.status.HTTP_202_ACCEPTED,
    response_model=utils.UserDetails,
)
async def update_user(
    to_update: utils.UserUpdate, token: str = fastapi.Depends(utils.oauth2_scheme)
) -> utils.UserDetails:
    """Endpoint used to update a users information"""

    # get variables for creating the token: if don't exist, raise exception ===
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

    # create a dictionary with only the fields that should be updated ===
    set_command = {}
    for k, v in to_update.dict().items():
        if v is not None:
            set_command[k] = v
    # ===

    # update the user in the database and return the user with the new information ===
    await user.update({"$set": set_command})

    return utils.UserDetails(**user.dict())
    # ===
