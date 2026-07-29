"""Outgoing calls of the showcase service."""

import typing

import aiohttp
import httpx
import niquests
import requests


PAYMENTS_API_URL: typing.Final = "https://payments.example.com"
DELIVERY_API_URL: typing.Final = "https://delivery.example.com"
REQUEST_TIMEOUT: typing.Final = 10

payments_client: typing.Final = httpx.AsyncClient(base_url=PAYMENTS_API_URL, timeout=REQUEST_TIMEOUT)


async def charge_payment(order_id: int, amount: int) -> dict:
    """Charge a payment for an order."""
    response = await payments_client.post("/charges", json={"order": order_id, "amount": amount})
    return response.json()


async def fetch_delivery_slots(city: str) -> dict:
    """Read available delivery slots."""
    async with aiohttp.ClientSession() as session, session.get(f"{DELIVERY_API_URL}/slots/{city}") as response:
        return await response.json()


def fetch_payment_status(payment_id: int) -> dict:
    """Read a payment status from the external payments API."""
    response = requests.get(f"{PAYMENTS_API_URL}/payments/{payment_id}", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def send_delivery_event(event: dict) -> dict:
    """Push a delivery event to the external delivery API."""
    with niquests.Session() as session:
        response = session.post(f"{DELIVERY_API_URL}/events", json=event, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
