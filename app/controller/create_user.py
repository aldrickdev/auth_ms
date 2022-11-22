# std
# 3p
import fastapi

# user
import exceptions
import utils
import queries

router = fastapi.APIRouter()


@router.post(
    path="/",
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def create_user(create_user_id: str, req_data: utils.UserCreateStepTwo) -> None:
    """Endpoint to complete the user creation process"""

    # check to see if the provided username is valid ===
    try:
        await utils.validate_username(req_data.username)

    except exceptions.InvalidUsernameError as err:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"{err}",
        )
    # ===

    # delete Create User record ===
    create_user_record = await queries.get_create_user_record_by_uuid(create_user_id)
    if create_user_record is None:
        raise exceptions.HTTPInvalidDataProvided

    user_email = create_user_record.user_email

    await queries.delete_create_user_record_by_id(str(create_user_record.id))
    # ===

    # === hash the provided password and add the user to the User Table
    hashed_password = await utils.hash_password(req_data.password)

    await queries.create_user_record(req_data.username, user_email, hashed_password)
