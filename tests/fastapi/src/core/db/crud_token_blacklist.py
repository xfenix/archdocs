from fastcrud import FastCRUD

from tests.fastapi.src.core.db.token_blacklist import TokenBlacklist
from tests.fastapi.src.core.schemas import TokenBlacklistCreate, TokenBlacklistUpdate


CRUDTokenBlacklist = FastCRUD[
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    None,
    None,
]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
