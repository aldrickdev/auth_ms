# 3p
import beanie


class ForgotPassword(beanie.Document):
    """The model that represents the users that are attempting to reset their password"""

    user_id: str
    uuid: str
    token: str
    datetime_created: str

    class Settings:
        name = "ForgotPasswords"
