title: str = "Auth MS"

description: str = """
Authentication Microservice built using FastAPI. It makes use of password hashing with 
HS256 and Bearer with JWT tokens.

This Microservice allows you to:
- Get Token
- Create Users
- Get Details of the logged in user
- Disable a User
- Update the users role (Not Implemented)
"""

version: str = "0.1.0"

# terms_of_service: str

contact = {
    "name": "Aldrick Castro",
    "email": "aldrickdev@gmail.com",
}

license_info = {"name": "MIT", "file": "LICENSE"}

tags_metadata = [
    {
        "name": "Users",
        "Description": "Operations that can be user to interact with the User database",
    },
    {"name": "Token", "Description": "Endpoint to get a token"},
]
