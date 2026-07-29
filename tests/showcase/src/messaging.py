"""FastStream brokers of the showcase service."""

import typing

from faststream import FastStream
from faststream.kafka import KafkaBroker
from faststream.nats import NatsBroker
from faststream.rabbit import RabbitBroker
from faststream.redis import RedisBroker


rabbit_broker: typing.Final = RabbitBroker("amqp://showcase:password@rabbit.internal:5672/")
kafka_broker: typing.Final = KafkaBroker("kafka.internal:9092")
nats_broker: typing.Final = NatsBroker("nats://nats.internal:4222")
redis_broker: typing.Final = RedisBroker("redis://cache.internal:6379/2")

faststream_app: typing.Final = FastStream(rabbit_broker)


@rabbit_broker.subscriber("order-commands")
async def handle_order_command(command: dict) -> None:
    """Consume order commands from RabbitMQ."""
    await kafka_broker.publish(command, topic="order-events")


@kafka_broker.subscriber("payment-events")
async def handle_payment_event(event: dict) -> None:
    """Consume payment events from Kafka."""
    await nats_broker.publish(event, subject="orders.paid")


@nats_broker.subscriber("orders.paid")
async def handle_paid_order(event: dict) -> None:
    """Consume paid orders from NATS."""
    await redis_broker.publish(event, channel="search-index")


@redis_broker.subscriber("search-index")
async def handle_search_index(event: dict) -> None:
    """Consume search index events from Redis streams."""


@rabbit_broker.publisher("order-replies")
async def publish_order_reply(reply: dict) -> dict:
    """Publish a reply back to RabbitMQ."""
    return reply
