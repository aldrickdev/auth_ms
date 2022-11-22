import os

import exceptions


all_envs = [
    "ENV",
    "FRONTEND_URL",
    "ALGORITHM",
    "SECRET_KEY",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "MONGO_CONNECTION",
    "AWS_REGION",
    "AWS_SEND_EMAIL_ACCESS_KEY",
    "AWS_SEND_EMAIL_SECRET_KEY",
]


def init_env_vars() -> None:
    """Figures out if the environment variables should be pulled from the system or .env file"""

    env = os.environ.get("ENV")

    if env is None:
        from dotenv import load_dotenv, find_dotenv

        env_file_location = find_dotenv()

        if not env_file_location:
            raise FileNotFoundError("Running Locally with no .env file")

        load_dotenv(env_file_location)

    verify_env_vars()


def verify_env_vars() -> None:
    """Verify that all required environment variables are present for the application to run"""

    results = list(map(verify_single_env_var, all_envs))

    if not all(results):
        raise exceptions.MissingEnvironmentVariables


def verify_single_env_var(env_string: str) -> bool:
    """Return true if the environment variable exist is the current environment else return false"""

    result = os.environ.get(env_string)

    if result is not None and result != "":
        return True

    return False


init_env_vars()


ENV = os.environ.get("ENV")
FRONTEND_URL = os.environ.get("FRONTEND_URL")
ALGORITHM = os.environ.get("ALGORITHM")
SECRET_KEY = os.environ.get("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
MONGO_CONNECTION = os.environ.get("MONGO_CONNECTION")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_SEND_EMAIL_ACCESS_KEY = os.environ.get("AWS_SEND_EMAIL_ACCESS_KEY")
AWS_SEND_EMAIL_SECRET_KEY = os.environ.get("AWS_SEND_EMAIL_SECRET_KEY")
