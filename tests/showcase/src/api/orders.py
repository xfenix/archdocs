"""Public HTTP API of the showcase service."""

import typing

from fastapi import APIRouter


orders_router: typing.Final = APIRouter(prefix="/orders", tags=["orders"])


@orders_router.get("/")
async def list_orders() -> list[dict]:
    """List orders of the current customer."""
    return []


@orders_router.post("/")
async def place_order(order: dict) -> dict:
    """Place a new order."""
    return order


@orders_router.put("/{order_id}")
async def replace_order(order_id: int, order: dict) -> dict:
    """Replace an order with a new revision."""
    return {"id": order_id, **order}


@orders_router.patch("/{order_id}")
async def update_order(order_id: int, order: dict) -> dict:
    """Update a part of an order."""
    return {"id": order_id, **order}


@orders_router.delete("/{order_id}")
async def cancel_order(order_id: int) -> None:
    """Cancel an order."""
