# standard imports
import asyncio
from typing import Any

# third party imports
from httpx import AsyncClient

# user imports
from main import app


def event_loop_wrapper(func):
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        task = loop.create_task(func(*args, **kwargs))
        return await task

    return wrapper


@event_loop_wrapper
async def get_user_token(username: str, password: str) -> dict[str, str]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/user/token",
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f"grant_type=&username={username}&password={password}&scope=&client_id=&\
client_secret=",
        )

    return response


@event_loop_wrapper
async def create(username: str, email: str, password: str) -> dict[str, str]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/user/create",
            headers={"Content-Type": "application/json"},
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

    return response


@event_loop_wrapper
async def get_user_details(token: str) -> dict[str, str]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/user/details",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        )

    return response


@event_loop_wrapper
async def edit_user(token: str, update: dict[Any, Any]) -> dict[str, str]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/api/v1/user/edit",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json=update,
        )

    return response


@event_loop_wrapper
async def disable_user(token: str) -> dict[str, str]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/api/v1/user/disable",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

    return response


@event_loop_wrapper
async def update_password(token: str, password: str) -> dict[str, str]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/api/v1/user/update-password",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={"password": password},
        )

    return response
