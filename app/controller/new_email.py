# std
import uuid

# 3p
import pydantic
import fastapi

# user
import env_vars
import queries
import email_handler


router = fastapi.APIRouter()


@router.post(
    path="/",
    status_code=fastapi.status.HTTP_202_ACCEPTED,
)
async def new_user_email(provided_email: pydantic.EmailStr) -> None:
    """Endpoint used to begin the process of creating a user"""

    # check to see if the email already exist in the User Database: If it doesn't exist continue
    # else send an email to the user saying that they already have an existing account ===
    user = await queries.get_user_by_email(provided_email)
    if user is not None:
        email_handler.SESClient.send_email(
            FromEmailAddress="do-not-reply@greyminties.com",
            Destination={
                "ToAddresses": [
                    provided_email,
                ],
            },
            Content={
                "Template": {
                    "TemplateName": "Test_CreateUserExistingAccountV1",
                    "TemplateData": '{"url":"greyminties.com/forgot-password"}',
                }
            },
        )
        return None
    # ===

    # check if user with this email has already tried to create an account already, delete
    # their previous create user record ===
    record = await queries.get_create_user_record_by_user_email(provided_email)
    if record is not None:
        await record.delete()
    # ===

    # save the user email and a uuid in the Create User Table ===
    identifier = str(uuid.uuid5(uuid.uuid1(), provided_email))
    await queries.create_a_create_user_record(identifier, provided_email)
    # ===

    # email the user with a link that will have the uuid as a path parameter ===
    email_handler.SESClient.send_email(
        FromEmailAddress="do-not-reply@greyminties.com",
        Destination={
            "ToAddresses": [
                provided_email,
            ],
        },
        Content={
            "Template": {
                "TemplateName": "Test_NewUserV1",
                "TemplateData": f'{{"url":"{env_vars.FRONTEND_URL}/create-user/{identifier}"}}',
            }
        },
    )
    return None
    # ===
