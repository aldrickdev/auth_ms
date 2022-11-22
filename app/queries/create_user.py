# std
from typing import Optional
from datetime import datetime

# user
import env_vars
import models


async def create_a_create_user_record(unique_id: str, user_email: str) -> models.CreateUser:
    """Creates a create user record and then returns it"""

    current_ts = datetime.now().timestamp()
    delta_in_seconds = int(env_vars.ACCESS_TOKEN_EXPIRE_MINUTES) * 60

    instance = models.CreateUser(
        uuid=unique_id,
        user_email=user_email,
        creation_ts=current_ts,
        expiration_ts=current_ts + delta_in_seconds,
    )

    await instance.insert()


async def get_create_user_record_by_uuid(uuid: str) -> Optional[models.CreateUser]:
    """returns a create user record if one is found when searching by uuid, otherwise return None"""

    return await models.CreateUser.find_one(models.CreateUser.uuid == uuid)


async def get_create_user_record_by_id(record_id: str) -> Optional[models.CreateUser]:
    """returns a create user record if one is found when searching by id, otherwise return None"""

    return await models.CreateUser.get(record_id)


async def get_create_user_record_by_user_email(user_email: str) -> Optional[models.CreateUser]:
    """returns a create user record if one is found when searching by user email,
    otherwise return None"""

    return await models.CreateUser.find_one(models.CreateUser.user_email == user_email)


async def delete_create_user_record_by_id(record_id: str) -> None:
    """Attempts to find the record by id and then deleting it if found"""

    record = await get_create_user_record_by_id(record_id)

    if record is not None:
        await record.delete()


async def delete_create_user_record_by_uuid(uuid: str) -> None:
    """Attempts to find the record by id and then deleting it if found"""

    record = await get_create_user_record_by_uuid(uuid)

    if record is not None:
        await record.delete()
