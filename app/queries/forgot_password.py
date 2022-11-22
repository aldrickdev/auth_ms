# std
from datetime import datetime

# user
import models


async def get_forgot_password_attempt_by_user_id(user_id: str) -> models.ForgotPassword:
    """Returns a forgot password record after searching by id"""

    return await models.ForgotPassword.find_one(models.ForgotPassword.user_id == user_id)


async def get_forgot_password_attempt_by_id(record_id: str) -> models.ForgotPassword:
    """Returns a forgot password record after searching by id"""

    return await models.ForgotPassword.get(record_id)


async def get_forgot_password_attempt_by_uuid(uuid: str) -> models.ForgotPassword:
    """Returns a forgot password record after searching by uuid"""

    return await models.ForgotPassword.find_one(models.ForgotPassword.uuid == uuid)


async def save_forgot_password_attempt(user_id: str, uuid: str, token: str) -> None:
    """Creates a forgot password record"""

    datetime_created = str(datetime.utcnow())
    new_record = models.ForgotPassword(
        user_id=user_id, uuid=uuid, token=token, datetime_created=datetime_created
    )

    await new_record.insert()


async def delete_forgot_password_attempt_by_id(record_id: str) -> None:
    """Deletes the forgot password record by id"""

    record = await get_forgot_password_attempt_by_id(record_id)

    await record.delete()
