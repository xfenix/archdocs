import re as py_re

from experimental.fastarch import settings


SUBSCRIBER_DECORATOR_RE: py_re.Pattern = py_re.compile(r"@\w+\.subscriber\(", flags=settings.TYPICAL_RE_FLAGS)
PRODUCER_DECORATOR_RE: py_re.Pattern = py_re.compile(r"@\w+\.producer\(", flags=settings.TYPICAL_RE_FLAGS)


def find_faststream_features(raw_source: str) -> list[bool, bool]:
    consumer_producer_found = [False, False]
    if "faststream" not in raw_source:
        return []
    if SUBSCRIBER_DECORATOR_RE.search(raw_source):
        consumer_producer_found[0] = True
    if PRODUCER_DECORATOR_RE.search(raw_source):
        consumer_producer_found[1] = True
    return consumer_producer_found
