"""User routes for Litestar application."""

import typing

from litestar import Router, delete, get, patch, post
from litestar.datastructures import State


@get("/users")
async def list_users(state: State) -> dict[str, typing.Any]:
    """List all users."""
    return {"users": []}


@get("/users/{user_id:int}")
async def get_user(user_id: int, state: State) -> dict[str, typing.Any]:
    """Get user by ID."""
    return {"user_id": user_id}


@post("/users")
async def create_user(data: dict[str, typing.Any]) -> dict[str, str]:
    """Create a new user."""
    return {"message": "User created"}


@patch("/users/{user_id:int}")
async def update_user(user_id: int, data: dict[str, typing.Any]) -> dict[str, str]:
    """Update user."""
    return {"message": f"User {user_id} updated"}


@delete("/users/{user_id:int}")
async def delete_user(user_id: int) -> dict[str, str]:
    """Delete user."""
    return {"message": f"User {user_id} deleted"}


users_router: typing.Final = Router(
    path="/api/v1",
    route_handlers=[list_users, get_user, create_user, update_user, delete_user],
)
