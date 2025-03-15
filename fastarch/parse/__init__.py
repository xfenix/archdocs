import enum
import typing

from fastarch import http_api, messaging_queue


class FeaturesEnum(enum.Enum):
    fastapi = 1
    faststream = 2
    sqlalchemy = 3


MAP_OF_FEATURES: typing.Final = {
    FeaturesEnum.fastapi: http_api.find_fastapi_features,
    FeaturesEnum.faststream: messaging_queue.find_faststream_features,
}
