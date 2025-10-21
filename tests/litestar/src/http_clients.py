"""HTTP clients configuration."""

import typing

import aiohttp
import httpx


httpx_client: typing.Final = httpx.AsyncClient(base_url="https://api.example.com")


async def fetch_external_api_httpx(endpoint: str) -> dict:
    """Fetch data from external API using httpx."""
    async with httpx_client as client:
        response = await client.get(endpoint)
        return response.json()


async def fetch_external_api_aiohttp(endpoint: str) -> dict:
    """Fetch data from external API using aiohttp."""
    async with aiohttp.ClientSession() as session, session.get(f"https://api.example.com{endpoint}") as response:
        return await response.json()
