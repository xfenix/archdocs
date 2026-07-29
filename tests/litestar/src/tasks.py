"""Task queues configuration."""

import typing

import dramatiq
from celery import Celery
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from taskiq import InMemoryBroker


celery_app: typing.Final = Celery("litestar_app", broker="redis://localhost:6379/0")

taskiq_broker: typing.Final = InMemoryBroker()

dramatiq_broker: typing.Final = RabbitmqBroker(url="amqp://user:password@localhost:5672/")
dramatiq.set_broker(dramatiq_broker)


@celery_app.task
def send_email_task(email: str, subject: str) -> None:
    """Send email via Celery."""


@taskiq_broker.task
async def process_data_task(data: dict) -> None:
    """Process data via Taskiq."""


@dramatiq.actor(queue_name="reports")
def build_report_task(report_id: int) -> None:
    """Build a report via Dramatiq."""
