"""Item routes for Litestar application."""

import typing

from litestar import Router, get, post, put


@get("/items")
async def list_items() -> dict[str, list]:
    """List all items."""
    return {"items": []}


@get("/items/{item_id:int}")
async def get_item(item_id: int) -> dict[str, int]:
    """Get item by ID."""
    return {"item_id": item_id}


@post("/items")
async def create_item(data: dict[str, typing.Any]) -> dict[str, str]:
    """Create a new item."""
    return {"message": "Item created"}


@put("/items/{item_id:int}")
async def update_item(item_id: int, data: dict[str, typing.Any]) -> dict[str, str]:
    """Update item completely."""
    return {"message": f"Item {item_id} updated"}


items_router: typing.Final = Router(
    path="/api/v1",
    route_handlers=[list_items, get_item, create_item, update_item],
)
