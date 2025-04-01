from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fastapi.src.core.db.database import async_get_db
from tests.fastapi.src.core.exceptions.http_exceptions import UnauthorizedException
from tests.fastapi.src.core.security import blacklist_tokens, oauth2_scheme


router = APIRouter(tags=["login"])


@router.post("/logout")
async def logout(
    response: Response,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
    db: AsyncSession = Depends(async_get_db),
) -> dict[str, str]:
    try:
        if not refresh_token:
            msg = "Refresh token not found"
            raise UnauthorizedException(msg)

        await blacklist_tokens(access_token=access_token, refresh_token=refresh_token, db=db)
        response.delete_cookie(key="refresh_token")

        return {"message": "Logged out successfully"}

    except JWTError:
        msg = "Invalid token."
        raise UnauthorizedException(msg)
