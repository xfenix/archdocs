import dataclasses
import typing


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HTTPApiFeatures:
    served_methods: frozenset[str]
    served_methods_existed: bool
