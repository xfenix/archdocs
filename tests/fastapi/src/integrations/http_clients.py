from typing import Any

import niquests
import requests


PAYMENTS_API_URL = "https://payments.example.com"
BILLING_API_URL = "https://billing.example.com"
REQUEST_TIMEOUT = 10


def fetch_payment_status(payment_id: int) -> dict[str, Any]:
    """Read a payment status from the external payments API."""
    response = requests.get(f"{PAYMENTS_API_URL}/payments/{payment_id}", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def send_billing_event(event: dict[str, Any]) -> dict[str, Any]:
    """Push a billing event to the external billing API."""
    with niquests.Session() as session:
        response = session.post(f"{BILLING_API_URL}/events", json=event, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
