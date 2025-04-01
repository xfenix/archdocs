import dataclasses
import typing


@typing.final
@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HTTPApiFeatures:
    in_methods: frozenset[str]
    out_methods: frozenset[str]
    in_methods_existed: bool
    out_methods_existed: bool
