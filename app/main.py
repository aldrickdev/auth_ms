# standard imports

# third party imports
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# user imports
import database
import env_vars
import models
import router

# creates a FastAPI instance
app = fastapi.FastAPI(
    title="Greymint Authentication",
    version="0.0.1",
    openapi_tags=[
        {
            "name": "User",
            "Description": "Operations that can be user to interact with the User database",
        },
    ],
    docs_url=None,
)

origins = [env_vars.FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    path="/",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["Index"],
)
def index() -> str:
    return f"Application Verison {app.version} running in the {env_vars.ENV} environment"


router.add_routers(app, "/api")


@app.on_event("startup")
async def server_startup() -> None:
    print("Server start up")
    mongo_models = [models.User, models.ForgotPassword, models.CreateUser]
    await database.init_db(mongo_models)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, log_level="info")
