import re as py_re
import types
import typing

from archdocs import prefilter, settings
from archdocs.features.messaging_queue import const


_SUBSCRIBER_DECORATOR_PATTERN: typing.Final = py_re.compile(r"@\w+\.subscriber\(", flags=settings.TYPICAL_RE_FLAGS)
# The `\b` is not decoration: without it every position inside a long word run — a base64 blob
# in a string is enough — starts its own `\w+` attempt, and one file costs seconds instead of
# microseconds.
_PRODUCER_PATTERN: typing.Final = py_re.compile(
    r"(?:@\w+\.(?:publisher|producer)|\b\w+\.publish)\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
_BROKER_PATTERNS: typing.Final = types.MappingProxyType(
    {
        one_broker: py_re.compile(
            rf"\bfaststream\.{one_broker.value}\b",
            flags=settings.TYPICAL_RE_FLAGS,
        )
        for one_broker in const.BrokerEnum
    },
)
# A broker assignment always opens its line, and the anchor is what caps the cost: unanchored,
# every position of a long word run starts a `\w+` attempt that backtracks hunting for `=`.
_BROKER_VARIABLE_PATTERN: typing.Final = py_re.compile(
    r"^[ \t]*(?P<variable>\w+)\s*(?::[^=\n]+)?=\s*(?P<broker_class>\w+)\s*\(",
    flags=settings.TYPICAL_RE_FLAGS,
)
# A flow belongs to the broker whose variable is decorated, not to the file: a broker somebody
# imported next to a working one is not something the service consumes from, and an arrow drawn
# for it is a dependency the reader has no way to disprove.
_FLOW_PATTERNS_OF_DIRECTION: typing.Final = types.MappingProxyType(
    {
        const.MessageDirection.consumed: (
            py_re.compile(r"@(?P<variable>\w+)\.subscriber\(", flags=settings.TYPICAL_RE_FLAGS),
        ),
        const.MessageDirection.produced: (
            py_re.compile(r"@(?P<variable>\w+)\.(?:publisher|producer)\(", flags=settings.TYPICAL_RE_FLAGS),
            py_re.compile(r"\b(?P<variable>\w+)\.publish\(", flags=settings.TYPICAL_RE_FLAGS),
        ),
    },
)
_TOPIC_PATTERNS_OF_DIRECTION: typing.Final = types.MappingProxyType(
    {
        const.MessageDirection.consumed: (
            py_re.compile(
                r"@(?P<variable>\w+)\.subscriber\(\s*[\"'](?P<topic>[^\"']+)[\"']",
                flags=settings.TYPICAL_RE_FLAGS,
            ),
        ),
        const.MessageDirection.produced: (
            py_re.compile(
                r"@(?P<variable>\w+)\.publisher\(\s*[\"'](?P<topic>[^\"']+)[\"']",
                flags=settings.TYPICAL_RE_FLAGS,
            ),
            py_re.compile(
                r"(?P<variable>\w+)\.publish\([^()]*?\b(?:"
                + "|".join(const.DESTINATION_KEYWORDS)
                + r")\s*=\s*[\"'](?P<topic>[^\"']+)[\"']",
                flags=settings.TYPICAL_RE_FLAGS,
            ),
        ),
    },
)
_BROKER_NAME_OF_CLASS: typing.Final = types.MappingProxyType(
    {one_broker_class: one_broker.value for one_broker, one_broker_class in const.BROKER_CLASS_OF_NAME.items()},
)
_FASTSTREAM_LITERALS: typing.Final = ("faststream",)
_EMPTY_FEATURES: typing.Final = const.MessagingQueueFeatures()


def _collect_broker_of_variable(raw_source: str, /) -> dict[str, str]:
    return {
        one_match.group("variable"): _BROKER_NAME_OF_CLASS[one_match.group("broker_class")]
        for one_match in _BROKER_VARIABLE_PATTERN.finditer(raw_source)
        if one_match.group("broker_class") in _BROKER_NAME_OF_CLASS
    }


def _collect_topics_of_broker(
    raw_source: str,
    broker_of_variable: typing.Mapping[str, str],
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


def _has_any_flow(
    raw_source: str,
    broker_of_variable: typing.Mapping[str, str],
    message_direction: const.MessageDirection,
    broker_name: str,
    /,
) -> bool:
    return any(
        broker_of_variable.get(one_match.group("variable")) == broker_name
        for one_pattern in _FLOW_PATTERNS_OF_DIRECTION[message_direction]
        for one_match in one_pattern.finditer(raw_source)
    )


def _build_broker_flow(
    raw_source: str,
    broker_of_variable: typing.Mapping[str, str],
    broker_name: str,
    /,
) -> const.BrokerFlow:
    return const.BrokerFlow(
        broker_name=broker_name,
        consumes=_has_any_flow(raw_source, broker_of_variable, const.MessageDirection.consumed, broker_name),
        produces=_has_any_flow(raw_source, broker_of_variable, const.MessageDirection.produced, broker_name),
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


def find_faststream_features(raw_source: str) -> const.MessagingQueueFeatures:
    if not prefilter.contains_any_literal(raw_source.lower(), _FASTSTREAM_LITERALS):
        return _EMPTY_FEATURES
    if not _SUBSCRIBER_DECORATOR_PATTERN.search(raw_source) and not _PRODUCER_PATTERN.search(raw_source):
        return _EMPTY_FEATURES
    broker_of_variable: typing.Final = _collect_broker_of_variable(raw_source)
    return const.MessagingQueueFeatures(
        broker_flows=tuple(
            _build_broker_flow(raw_source, broker_of_variable, one_broker.value)
            for one_broker, one_pattern in _BROKER_PATTERNS.items()
            if one_pattern.search(raw_source)
        ),
    )
