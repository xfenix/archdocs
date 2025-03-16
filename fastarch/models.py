import dataclasses


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class HTTPApiFeatures:
    in_methods: list[str]
    out_methods: list[str]
    in_methods_existed: bool
    out_methods_existed: bool


@dataclasses.dataclass(slots=True, kw_only=True, frozen=True)
class MQFeatures:
    consumers: bool
    producers: bool
    brokers: list[str]
