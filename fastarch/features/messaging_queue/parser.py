import re as py_re
import types
import typing

from fastarch import settings
from fastarch.features.messaging_queue import const


_SUBSCRIBER_DECORATOR_RE: typing.Final = py_re.compile(r"@\w+\.subscriber\(", flags=settings.TYPICAL_RE_FLAGS)
_PRODUCER_RE: typing.Final = py_re.compile(
    r"(?:@\w+\.(?:publisher|producer)|\w+\.publish)\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
_BROKER_PATTERNS: typing.Final = types.MappingProxyType(
    {
        one_broker: py_re.compile(
            rf"\bfaststream\.{one_broker.value}\b",
            flags=settings.TYPICAL_RE_FLAGS,
        )
        for one_broker in const.BrokersEnum
    },
)
_BROKER_VARIABLE_PATTERN: typing.Final = py_re.compile(
    r"(?P<variable>\w+)\s*(?::[^=\n]+)?=\s*(?P<broker_class>\w+)\s*\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
_SUBSCRIBED_TOPIC_PATTERN: typing.Final = py_re.compile(
    r"@(?P<variable>\w+)\.subscriber\(\s*[\"'](?P<topic>[^\"']+)[\"']",
    flags=settings.TYPICAL_RE_FLAGS,
)
_PUBLISHED_TOPIC_PATTERN: typing.Final = py_re.compile(
    r"@(?P<variable>\w+)\.publisher\(\s*[\"'](?P<topic>[^\"']+)[\"']",
    flags=settings.TYPICAL_RE_FLAGS,
)
_DESTINATION_ALTERNATIVES: typing.Final = "|".join(const.DESTINATION_KEYWORDS)
_PUBLISH_CALL_PATTERN: typing.Final = py_re.compile(
    r"(?P<variable>\w+)\.publish\([^()]*?"
    rf"\b(?:{_DESTINATION_ALTERNATIVES})\s*=\s*[\"'](?P<topic>[^\"']+)[\"']",
    flags=settings.TYPICAL_RE_FLAGS,
)
_TOPIC_PATTERNS_OF_DIRECTION: typing.Final = types.MappingProxyType(
    {
        const.MessageDirection.consumed: (_SUBSCRIBED_TOPIC_PATTERN,),
        const.MessageDirection.produced: (_PUBLISHED_TOPIC_PATTERN, _PUBLISH_CALL_PATTERN),
    },
)
_BROKER_NAME_OF_CLASS: typing.Final = types.MappingProxyType(
    {one_broker_class: one_broker.value for one_broker, one_broker_class in const.BROKER_CLASS_OF_NAME.items()},
)
_EMPTY_FEATURES: typing.Final = const.MQFeatures()


def _collect_broker_of_variable(raw_source: str, /) -> dict[str, str]:
    return {
        one_match.group("variable"): _BROKER_NAME_OF_CLASS[one_match.group("broker_class")]
        for one_match in _BROKER_VARIABLE_PATTERN.finditer(raw_source)
        if one_match.group("broker_class") in _BROKER_NAME_OF_CLASS
    }


def _collect_topics_of_broker(
    raw_source: str,
    broker_of_variable: dict[str, str],
    message_direction: const.MessageDirection,
    broker_name: str,
    /,
) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            one_match.group("topic")
            for one_pattern in _TOPIC_PATTERNS_OF_DIRECTION[message_direction]
            for one_match in one_pattern.finditer(raw_source)
            if broker_of_variable.get(one_match.group("variable")) == broker_name
        ),
    )


def _build_broker_flow(raw_source: str, broker_of_variable: dict[str, str], broker_name: str, /) -> const.BrokerFlow:
    return const.BrokerFlow(
        broker_name=broker_name,
        consumes=bool(_SUBSCRIBER_DECORATOR_RE.search(raw_source)),
        produces=bool(_PRODUCER_RE.search(raw_source)),
        consumed_topics=_collect_topics_of_broker(
            raw_source,
            broker_of_variable,
            const.MessageDirection.consumed,
            broker_name,
        ),
        produced_topics=_collect_topics_of_broker(
            raw_source,
            broker_of_variable,
            const.MessageDirection.produced,
            broker_name,
        ),
    )


def find_faststream_features(raw_source: str) -> const.MQFeatures:
    if "faststream" not in raw_source:
        return _EMPTY_FEATURES
    if not _SUBSCRIBER_DECORATOR_RE.search(raw_source) and not _PRODUCER_RE.search(raw_source):
        return _EMPTY_FEATURES
    broker_of_variable: typing.Final = _collect_broker_of_variable(raw_source)
    return const.MQFeatures(
        broker_flows=tuple(
            _build_broker_flow(raw_source, broker_of_variable, one_broker.value)
            for one_broker, one_pattern in _BROKER_PATTERNS.items()
            if one_pattern.search(raw_source)
        ),
    )
