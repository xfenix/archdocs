import dataclasses
import enum
import re as py_re
import typing

from experimental.fastarch import settings


class BrokersEnum(enum.Enum):
    RABBIT = "rabbit"
    KAFKA = "kafka"
    NATS = "nats"
    REDIS = "redis"


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    consumers: bool
    producers: bool
    brokers: list[str]


_SUBSCRIBER_DECORATOR_RE: typing.Final = py_re.compile(r"@\w+\.subscriber\(", flags=settings.TYPICAL_RE_FLAGS)
_PRODUCER_DECORATOR_RE: typing.Final = py_re.compile(
    r"@\w+\.producer\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
_BROKER_PATTERNS: typing.Final = {
    broker: py_re.compile(
        rf"\b(?:from\s+faststream(?:\s+import\s+|\.{broker.value}\s+import\s+)|import\s+faststream\.{broker.value}\b)",
        flags=settings.TYPICAL_RE_FLAGS,
    )
    for broker in BrokersEnum
}


def find_faststream_features(raw_source: str) -> MQFeatures:
    if "faststream" not in raw_source:
        return MQFeatures(
            consumers=False,
            producers=False,
            brokers=[],
        )
    return MQFeatures(
        consumers=bool(_SUBSCRIBER_DECORATOR_RE.search(raw_source)),
        producers=bool(_PRODUCER_DECORATOR_RE.search(raw_source)),
        brokers=[broker.value for broker, pattern in _BROKER_PATTERNS.items() if pattern.search(raw_source)],
    )
