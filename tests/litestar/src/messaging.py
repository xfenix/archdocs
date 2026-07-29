"""Messaging queues configuration with FastStream."""

import typing

from faststream import FastStream
from faststream.kafka import KafkaBroker
from faststream.rabbit import RabbitBroker


rabbit_broker: typing.Final = RabbitBroker("amqp://user:password@localhost:5672/")
kafka_broker: typing.Final = KafkaBroker("localhost:9092")

faststream_app: typing.Final = FastStream(rabbit_broker)


@rabbit_broker.subscriber("user-commands")
async def handle_user_command(command: dict) -> None:
    """Consume user commands from RabbitMQ."""
    await kafka_broker.publish(command, topic="user-events")


@kafka_broker.subscriber("item-events")
async def handle_item_event(event: dict) -> None:
    """Consume item events from Kafka."""


@rabbit_broker.publisher("user-replies")
async def publish_user_reply(reply: dict) -> dict:
    """Publish a reply back to RabbitMQ."""
    return reply
