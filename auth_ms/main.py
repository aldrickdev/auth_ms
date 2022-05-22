from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer


app = FastAPI()

# This is what it used to tell FastAPI that a route is protected and will need
# the user to provide a token. The parameter tokenUrl tells the
# OAuthPasswordBearer that to obtain a token, the user will need to use the
# endpoint token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Using the oauth2_scheme as a dependency for this route, telling FastAPI that
# this route is protected
# The way that this works it that when a request hits /protected, the
# 0auth2_scheme dependency will look to see if the request has an Authorization
# header, it then checks if the value is Bearer plus a token and then return
# that token as a string to the function handling the request.
# If it doesn't see the Authrization header or the value doesn't have a Bearer
# token then it will response with a 401 status code
@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    return {"token": token}
