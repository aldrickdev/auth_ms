# std
import uuid

# 3p
import fastapi

# user
import env_vars
import exceptions
import email_handler
import queries
import utils

router = fastapi.APIRouter()


@router.post(
    path="/",
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def forgot_password(req: utils.UserForgotPasswordRequest) -> None:
    """Endpoint used to handle users that have forgotten their password"""

    # get user from database: if no user found, raise exception ===
    user = await queries.get_user_by_email(req.email)

    if user is None:
        raise exceptions.HTTPUserWasNotFound
    # ===

    # get forgot password record from database: if found, delete it ===
    record = await queries.get_forgot_password_attempt_by_user_id(str(user.id))

    if record is not None:
        await queries.delete_forgot_password_attempt_by_id(str(record.id))
    # ===

    # get variables for checking the token: if env vars don't exist, raise exception ===
    secret = env_vars.SECRET_KEY
    algorithm = env_vars.ALGORITHM
    # ===

    # create a uuid and jwt that will be saved in the forgot password db ===
    path_parameter = str(uuid.uuid5(uuid.uuid1(), user.email))
    token = await utils.create_token(user.email, 30, secret, algorithm)
    await queries.save_forgot_password_attempt(str(user.id), path_parameter, token)
    # ===

    # send email to user with url and jwt as a path parameter and return ===
    email_handler.SESClient.send_email(
        FromEmailAddress="do-not-reply@greyminties.com",
        Destination={
            "ToAddresses": [
                req.email,
            ],
        },
        Content={
            "Template": {
                "TemplateName": "Test_ForgotPasswordTemplateV3",
                "TemplateData": f'\
                {{"name":"{user.username}","url":"{env_vars.FRONTEND_URL}/reset-password/{path_parameter}"}}',
            }
        },
    )

    return None
    # ===
