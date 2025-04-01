from fastcrud import FastCRUD

from tests.fastapi.src.models.tier import Tier
from tests.fastapi.src.schemas.tier import TierCreateInternal, TierDelete, TierUpdate, TierUpdateInternal


CRUDTier = FastCRUD[Tier, TierCreateInternal, TierUpdate, TierUpdateInternal, TierDelete, None]
crud_tiers = CRUDTier(Tier)
