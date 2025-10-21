"""Task queues configuration."""

import typing

from celery import Celery
from taskiq import InMemoryBroker


celery_app: typing.Final = Celery("litestar_app", broker="redis://localhost:6379/0")

taskiq_broker: typing.Final = InMemoryBroker()


@celery_app.task
def send_email_task(email: str, subject: str) -> None:
    """Send email via Celery."""


@taskiq_broker.task
async def process_data_task(data: dict) -> None:
    """Process data via Taskiq."""
