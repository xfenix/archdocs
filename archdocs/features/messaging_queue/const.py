import dataclasses
import enum
import types
import typing


@typing.final
class BrokerEnum(enum.Enum):
    rabbit_broker = "rabbit"
    kafka_broker = "kafka"
    nats_broker = "nats"
    redis_broker = "redis"


BROKER_CLASS_OF_NAME: typing.Final = types.MappingProxyType(
    {
        BrokerEnum.rabbit_broker: "RabbitBroker",
        BrokerEnum.kafka_broker: "KafkaBroker",
        BrokerEnum.nats_broker: "NatsBroker",
        BrokerEnum.redis_broker: "RedisBroker",
    },
)
DESTINATION_KEYWORDS: typing.Final = ("queue", "topic", "subject", "channel", "stream", "list")


@typing.final
class MessageDirection(enum.Enum):
    consumed = "consumed"
    produced = "produced"


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class BrokerFlow:
    broker_name: str
    consumes: bool
    produces: bool
    consumed_topics: tuple[str, ...] = ()
    produced_topics: tuple[str, ...] = ()


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MessagingQueueFeatures:
    broker_flows: tuple[BrokerFlow, ...] = ()
