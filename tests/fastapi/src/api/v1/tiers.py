from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fastapi.src.api.dependencies import get_current_superuser
from tests.fastapi.src.core.db.database import async_get_db
from tests.fastapi.src.core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from tests.fastapi.src.crud.crud_tier import crud_tiers
from tests.fastapi.src.schemas.tier import TierCreate, TierCreateInternal, TierRead, TierUpdate


router = APIRouter(tags=["tiers"])


@router.post("/tier", dependencies=[Depends(get_current_superuser)], status_code=201)
async def write_tier(
    request: Request,
    tier: TierCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TierRead:
    tier_internal_dict = tier.model_dump()
    db_tier = await crud_tiers.exists(db=db, name=tier_internal_dict["name"])
    if db_tier:
        msg = "Tier Name not available"
        raise DuplicateValueException(msg)

    tier_internal = TierCreateInternal(**tier_internal_dict)
    created_tier: TierRead = await crud_tiers.create(db=db, object=tier_internal)
    return created_tier


@router.get("/tiers", response_model=PaginatedListResponse[TierRead])
async def read_tiers(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    tiers_data = await crud_tiers.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=TierRead,
    )

    response: dict[str, Any] = paginated_response(crud_data=tiers_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/tier/{name}", response_model=TierRead)
async def read_tier(request: Request, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    db_tier: TierRead | None = await crud_tiers.get(db=db, schema_to_select=TierRead, name=name)
    if db_tier is None:
        msg = "Tier not found"
        raise NotFoundException(msg)

    return db_tier


@router.patch("/tier/{name}", dependencies=[Depends(get_current_superuser)])
async def patch_tier(
    request: Request,
    values: TierUpdate,
    name: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_tier = await crud_tiers.get(db=db, schema_to_select=TierRead, name=name)
    if db_tier is None:
        msg = "Tier not found"
        raise NotFoundException(msg)

    await crud_tiers.update(db=db, object=values, name=name)
    return {"message": "Tier updated"}


@router.delete("/tier/{name}", dependencies=[Depends(get_current_superuser)])
async def erase_tier(request: Request, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_tier = await crud_tiers.get(db=db, schema_to_select=TierRead, name=name)
    if db_tier is None:
        msg = "Tier not found"
        raise NotFoundException(msg)

    await crud_tiers.delete(db=db, name=name)
    return {"message": "Tier deleted"}
