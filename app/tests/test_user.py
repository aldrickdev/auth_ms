# standard imports
import re
from typing import Any

# third party imports
import pytest
import pytest_asyncio

# user imports
from tests import helpers
from tests import constants
import env_vars
import database
import models
import utils


@pytest_asyncio.fixture
async def init_db_connection() -> None:
    """Initializes the connection to the database"""

    # get mongo_db credentials
    mongo_user = env_vars.MONGO_USER
    mongo_pwd = env_vars.MONGO_PWD

    # get database models
    mongo_models = [models.User]

    await database.init_db(mongo_user, mongo_pwd, mongo_models)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, email, password, status_code, result",
    [
        (  # Correct
            "aldrickcastro",
            "aldrick@greymint.com",
            "p@ssword",
            201,
            {
                "disabled": False,
                "email": "aldrick@greymint.com",
                "role": "standard",
                "username": "aldrickcastro",
            },
        ),
        (  # User already exist
            "aldrickcastro",
            "aldrick@greymint.com",
            "p@ssword",
            400,
            {"detail": "Provided Username is Already In Use"},
        ),
        (  # Username to short
            "aldrick",
            "aldrick@greymint.com",
            "p@ssword",
            422,
            {
                "detail": [
                    {
                        "ctx": {"limit_value": 8},
                        "loc": ["body", "username"],
                        "msg": "ensure this value has at least 8 characters",
                        "type": "value_error.any_str.min_length",
                    }
                ]
            },
        ),
        (  # Whitespace in username
            "aldrick castro",
            "aldrick@greymint.com",
            "p@ssword",
            400,
            {"detail": "Whitespaces Or Symbols Found In The Username"},
        ),
        (  # Symbols in username
            "aldrick%castro",
            "aldrick@greymint.com",
            "p@ssword",
            400,
            {"detail": "Whitespaces Or Symbols Found In The Username"},
        ),
        (  # Invalid email
            "aldrickcastro",
            "aldrick.com",
            "p@ssword",
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ],
            },
        ),
        (  # Password to small
            "aldrickcastro",
            "aldrick@greymint.com",
            "pass",
            422,
            {
                "detail": [
                    {
                        "ctx": {"limit_value": 8},
                        "loc": ["body", "password"],
                        "msg": "ensure this value has at least 8 characters",
                        "type": "value_error.any_str.min_length",
                    }
                ]
            },
        ),
    ],
)
async def test_create_user(
    init_db_connection,
    username: str,
    email: str,
    password: str,
    status_code: int,
    result: dict[Any, Any],
) -> None:
    """Test to see if we could create a user successfully"""

    # try to create the user
    response = await helpers.create(username, email, password)

    # test that the status code we get back when trying to create the user
    assert response.status_code == status_code

    # test that the json in the response is as expected
    assert response.json() == result


@pytest.mark.asyncio
async def test_user_token(init_db_connection) -> None:
    """Tests whether we get valid tokens when we provide a valid user and what happens when you
    provide a token for a non-existent user"""

    # === Check that we get a valid token when we provide a existing user ===
    # create the test user that will be used during the following tests
    username = "TestUser01"
    email = f"{username}@greymint.com"

    await helpers.create(username, email, constants.user_password)

    # try to get a token for the created user
    response = await helpers.get_user_token(username, constants.user_password)

    # pull data from the response to be used in the following tests
    json_response = response.json()
    token_in_response = json_response["access_token"]
    token_type = json_response["token_type"]

    # test that an access token is being returned for an existing user
    assert token_in_response is not None

    # test that the token matches the regular expression
    token_pattern = re.compile(r"[\w-]+\.[\w-]+\.[\w-]+")
    matches = token_pattern.findall(token_in_response)
    assert token_in_response == matches[0]

    # test that the access token type is bearer
    assert token_type is not None
    assert token_type == "bearer"

    # test that we get the correct username back when we decode the token
    decoded_username = await utils.get_username_from_jwt(
        token_in_response, constants.SECRET, constants.ALGORITHM
    )
    assert username == decoded_username
    # ===

    # === check that if a user provides an incorrect password that we get the proper response ===
    # create the user that will be used for the test
    username = "TestUser02"
    email = f"{username}@greymint.com"
    await helpers.create(username, email, constants.user_password)

    # try to get a token for the created user with an invalid password
    response = await helpers.get_user_token(username, "notthepassword")

    # test that for get an error
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Credentials"}
    # ===

    # === check that we are able to catch when the token is for a user that doesn't exist ===
    # user info being used for the test
    username = "doesntExist"

    # try to get a token for the user
    response = await helpers.get_user_token(username, constants.user_password)

    # test that the request fails
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Credentials"}
    # ===


@pytest.mark.asyncio
async def test_user_details(init_db_connection) -> None:
    """Tests that we get the correct user details from the server"""

    # === check that we get the expected user details back ===
    # create the test user that will be used during the following tests
    username = "TestUser03"
    email = f"{username}@greymint.com"
    await helpers.create(username, email, constants.user_password)

    # try to get a token for the created user
    response = await helpers.get_user_token(username, constants.user_password)
    token = response.json()["access_token"]

    # get user details using the token
    response = await helpers.get_user_details(token)

    # test that we get the expected user details
    assert response.status_code == 200
    assert response.json() == {
        "disabled": False,
        "email": email,
        "role": "standard",
        "username": username,
    }
    # ===

    # === check that we don't get any user details back if we provide a token for a user that
    # doesn't exist ===
    # create a token for a user that doesn't exist in the database
    username = "Dontexist"
    token_for_non_existent_user = await utils.create_token(
        username, 10, constants.SECRET, constants.ALGORITHM
    )

    # try to get user details
    response = await helpers.get_user_details(token_for_non_existent_user)

    # test that we get an error back
    assert response.status_code == 400
    assert response.json() == constants.not_found_response
    # ===


@pytest.mark.asyncio
async def test_update_user(init_db_connection) -> None:
    """Tests that we can update user details"""

    # === test that I can successfully update a users details ===
    # create a user that will be used for testing
    username = "TestUser04"
    email = f"{username}@greymint.com"
    await helpers.create(username, email, constants.user_password)

    # get a token for the user
    response = await helpers.get_user_token(username, constants.user_password)
    token = response.json()["access_token"]

    # update the users email
    new_email = f"new{username}@greymint.com"
    update = {"email": new_email}
    response = await helpers.edit_user(token, update)

    # tests that the email was successfully updated
    assert response.status_code == 202
    assert response.json() == {
        "disabled": False,
        "email": new_email,
        "role": "standard",
        "username": username,
    }
    # ===

    # === update the email and the role to see if multiple fields can be updated at once ===
    new_email = "new" + new_email
    new_role = "testing"
    update = {"email": new_email, "role": new_role}
    response = await helpers.edit_user(token, update)

    # tests that the email and the role was successfully updated
    assert response.status_code == 202
    assert response.json() == {
        "disabled": False,
        "email": new_email,
        "role": new_role,
        "username": username,
    }
    # ===

    # === check that trying to update fields on a user that doesn't exist fails ===
    # manually create a token for a fake user
    non_existent_username = "FakeUser"
    token_for_non_existent_user = await utils.create_token(
        non_existent_username, 10, constants.SECRET, constants.ALGORITHM
    )

    # send a request to update the user email
    update = {"email": "new@email.com"}
    response = await helpers.edit_user(token_for_non_existent_user, update)

    # tests that this operation fails
    assert response.status_code == 400
    assert response.json() == constants.not_found_response
    # ===


@pytest.mark.asyncio
async def test_disable_user(init_db_connection) -> None:
    """Check to see if we can properly disable a user"""

    # === check that we can disable an existent user ===
    # create a user that will be used for testing
    username = "TestUser05"
    email = f"{username}@greymint.com"
    await helpers.create(username, email, constants.user_password)

    # get a token for the user
    response = await helpers.get_user_token(username, constants.user_password)
    token = response.json()["access_token"]

    # disable the user
    response = await helpers.disable_user(token)

    # tests that we successfully disabled the user
    assert response.status_code == 202
    assert response.json() == {
        "disabled": True,
        "email": email,
        "role": "standard",
        "username": username,
    }
    # ===

    # === check that a trying to disable a user that doesn't exist fails ===
    # manually create a token for a user that doesn't exist
    non_existent_username = "FakeUser"
    token_for_non_existent_user = await utils.create_token(
        non_existent_username, 10, constants.SECRET, constants.ALGORITHM
    )

    # try to disable the user using the token
    response = await helpers.disable_user(token_for_non_existent_user)

    # tests that this operation fails
    assert response.status_code == 400
    assert response.json() == constants.not_found_response
    # ===


@pytest.mark.asyncio
async def test_update_password(init_db_connection) -> None:
    """Checks to see if when the password is actually being updated"""

    # === Check that when we update a password, we can get a token successfully ===
    # create test user
    username = "TestUser06"
    email = f"{username}@greymint.com"
    await helpers.create(username, email, constants.user_password)

    # get a token for the user
    response = await helpers.get_user_token(username, constants.user_password)
    token = response.json()["access_token"]

    # update users password
    new_password = f"new{constants.user_password}"
    response = await helpers.update_password(token, new_password)

    # test that we get the expected response
    assert response.status_code == 202
    assert response.json() == {
        "disabled": False,
        "email": email,
        "role": "standard",
        "username": username,
    }

    # get a new user token with the new password
    response = await helpers.get_user_token(username, new_password)
    token_from_new_password = response.json()["access_token"]

    # test that we get a proper token in the response
    token_pattern = re.compile(r"[\w-]+\.[\w-]+\.[\w-]+")
    matches = token_pattern.findall(token_from_new_password)
    assert token_from_new_password == matches[0]
    # ===

    # === Check that providing an invalid password fails to update the password ===
    # create test user
    username = "TestUser07"
    email = f"{username}@greymint.com"
    await helpers.create(username, email, constants.user_password)

    # get a token for the user
    response = await helpers.get_user_token(username, constants.user_password)
    token = response.json()["access_token"]

    # update users password with an invalid password
    invalid_password = "short"
    response = await helpers.update_password(token, invalid_password)

    # test that we get the expected response
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"limit_value": 8},
                "loc": ["body", "password"],
                "msg": "ensure this value has at least 8 characters",
                "type": "value_error.any_str.min_length",
            }
        ]
    }
    # ===

    # === Check that providing a token of a non-existent user provides results in an error ===
    # manually create a token for a non-existent user
    non_existent_username = "FakeUser"
    token_for_non_existent_user = await utils.create_token(
        non_existent_username, 10, constants.SECRET, constants.ALGORITHM
    )

    # try to update the password on the non-existent user
    response = await helpers.update_password(token_for_non_existent_user, constants.user_password)

    # test that we get the expected response
    assert response.status_code == 400
    assert response.json() == constants.not_found_response
    # ===
