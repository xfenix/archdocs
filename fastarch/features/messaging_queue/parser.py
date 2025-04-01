import re as py_re
import types
import typing

from fastarch import settings
from fastarch.features.messaging_queue import const


_SUBSCRIBER_DECORATOR_RE: typing.Final = py_re.compile(r"@\w+\.subscriber\(", flags=settings.TYPICAL_RE_FLAGS)
_PRODUCER_DECORATOR_RE: typing.Final = py_re.compile(
    r"@\w+\.producer\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
_BROKER_PATTERNS: typing.Final = types.MappingProxyType(
    {
        broker: py_re.compile(
            rf"\b(?:from\s+faststream(?:\s+import\s+|\.{broker.value}\s+import\s+)|import\s+faststream\.{broker.value}\b)",
            flags=settings.TYPICAL_RE_FLAGS,
        )
        for broker in const.BrokersEnum
    },
)


def find_faststream_features(raw_source: str) -> const.MQFeatures:
    if "faststream" not in raw_source:
        return const.MQFeatures(
            consumers=False,
            producers=False,
            brokers=[],
        )
    return const.MQFeatures(
        consumers=bool(_SUBSCRIBER_DECORATOR_RE.search(raw_source)),
        producers=bool(_PRODUCER_DECORATOR_RE.search(raw_source)),
        brokers=[broker.value for broker, pattern in _BROKER_PATTERNS.items() if pattern.search(raw_source)],
    )
