# std
# 3p
import fastapi

# user
import controller


def add_routers(app: fastapi.FastAPI, base_url: str) -> None:
    app.include_router(
        controller.get_details_router,
        prefix=f"{base_url}/v1/user/details",
        tags=["User"],
    )
    app.include_router(
        controller.get_token_router,
        prefix=f"{base_url}/v1/user/token",
        tags=["User"],
    )
    app.include_router(
        controller.new_email_router,
        prefix=f"{base_url}/v1/user/new-email",
        tags=["User"],
    )
    app.include_router(
        controller.create_user_router,
        prefix=f"{base_url}/v1/user/new-user/{{create_user_id}}",
        tags=["User"],
    )
    app.include_router(
        controller.forgot_password_router,
        prefix=f"{base_url}/v1/user/forgot-password",
        tags=["User"],
    )
    app.include_router(
        controller.reset_password_router,
        prefix=f"{base_url}/v1/user/reset-password/{{forgot_password_uuid}}",
        tags=["User"],
    )
    app.include_router(
        controller.disable_user_router,
        prefix=f"{base_url}/v1/user/disable",
        tags=["User"],
    )
    app.include_router(
        controller.edit_user_router,
        prefix=f"{base_url}/v1/user/edit",
        tags=["User"],
    )
    app.include_router(
        controller.update_password_router,
        prefix=f"{base_url}/v1/user/update-password",
        tags=["User"],
    )
