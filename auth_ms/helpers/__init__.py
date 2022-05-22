from auth_ms.models.user import User


def fake_decode_token(token: str) -> User:
    """Takes the token, decodes it and returns the user information

    Args:
        token (str): The token sued to find the user

    Returns:
        User: The user that the token points too
    """
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )
