from fastcrud import FastCRUD

from tests.fastapi.src.models.rate_limit import RateLimit
from tests.fastapi.src.schemas.rate_limit import (
    RateLimitCreateInternal,
    RateLimitDelete,
    RateLimitUpdate,
    RateLimitUpdateInternal,
)


CRUDRateLimit = FastCRUD[
    RateLimit,
    RateLimitCreateInternal,
    RateLimitUpdate,
    RateLimitUpdateInternal,
    RateLimitDelete,
    None,
]
crud_rate_limits = CRUDRateLimit(RateLimit)
