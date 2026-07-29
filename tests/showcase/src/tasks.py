"""Background tasks of the showcase service."""

import typing

import dramatiq
from arq.connections import RedisSettings
from celery import Celery
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from huey import RedisHuey
from rq import Queue
from taskiq import InMemoryBroker

from tests.showcase.src.cache import queue_connection


celery_app: typing.Final = Celery("showcase", broker="amqp://showcase:password@rabbit.internal:5672/")

taskiq_broker: typing.Final = InMemoryBroker()

dramatiq_broker: typing.Final = RabbitmqBroker(url="amqp://showcase:password@rabbit.internal:5672/")
dramatiq.set_broker(dramatiq_broker)

huey_app: typing.Final = RedisHuey("showcase", host="cache.internal", port=6379, db=4)

emails_queue: typing.Final = Queue("emails", connection=queue_connection)

ARQ_SETTINGS: typing.Final = RedisSettings(host="cache.internal", port=6379, database=5)


@celery_app.task
def send_receipt(order_id: int) -> None:
    """Send a receipt, executed by the celery worker."""


@taskiq_broker.task
async def recalculate_totals(order_id: int) -> None:
    """Recalculate order totals, executed by the taskiq worker."""


@dramatiq.actor(queue_name="reports")
def build_sales_report(report_id: int) -> None:
    """Build a sales report, executed by the dramatiq worker."""


@huey_app.task()
def drop_expired_carts() -> None:
    """Drop expired carts, executed by the huey worker."""


async def warm_up_catalogue(context: dict) -> None:
    """Warm the catalogue up, executed by the arq worker."""


def enqueue_order_email(order_id: int) -> str:
    """Put an order email into the queue served by the rq worker."""
    return emails_queue.enqueue(send_order_email, order_id).id


def send_order_email(order_id: int) -> None:
    """Send an order email."""
