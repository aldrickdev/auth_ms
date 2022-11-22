# user imports
import env_vars

# used for creating tokens
SECRET = env_vars.SECRET_KEY
ALGORITHM = env_vars.ALGORITHM

# the same password is used for all test users
user_password = "p@ssword"

# common json response
not_found_response = {"detail": "User Was Not Found"}
