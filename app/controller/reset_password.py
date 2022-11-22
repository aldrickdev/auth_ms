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


@router.post(
    path="/",
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def reset_password(
    forgot_password_uuid: str, req_data: utils.UserResetPasswordRequest
) -> None:
    """Endpoint used to handle resetting a password"""

    # get forgot password record: if None, raise exception; if found, delete it
    record = await queries.get_forgot_password_attempt_by_uuid(forgot_password_uuid)

    if record is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid Request to Reset Password",
        )

    await queries.delete_forgot_password_attempt_by_id(str(record.id))
    # ===

    # get variables for checking the token: if env vars don't exist, raise exception ===
    secret = env_vars.SECRET_KEY
    algorithm = env_vars.ALGORITHM
    # ===

    # decode the JWT to get the users email: if error while decoding token, raise exception ===
    token = record.token

    try:
        email = await utils.get_data_from_jwt(token, secret, algorithm)

    except (jose.JWTError, jose.jwt.ExpiredSignatureError, jose.jwt.JWTClaimsError) as err:
        raise exceptions.create_http_jwterror(err)
    # ===

    # get user from the database: if None, raise exception ===
    user = await queries.get_user_by_email(email)

    if user is None:
        raise exceptions.HTTPUserWasNotFound
    # ===

    # hash the password, update the database and return ===
    hashed_password = await utils.hash_password(req_data.password)
    await user.update({"$set": {"hashed_password": hashed_password}})

    return None
    # ===
