# third party imports
import beanie


class CreateUser(beanie.Document):
    """The model the represents the User that is trying to create an account"""

    uuid: str
    user_email: str
    creation_ts: float
    expiration_ts: float

    class Settings:
        name = "CreateUser"
