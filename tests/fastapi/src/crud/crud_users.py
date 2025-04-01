from fastcrud import FastCRUD

from tests.fastapi.src.models.user import User
from tests.fastapi.src.schemas.user import UserCreateInternal, UserDelete, UserUpdate, UserUpdateInternal


CRUDUser = FastCRUD[User, UserCreateInternal, UserUpdate, UserUpdateInternal, UserDelete, None]
crud_users = CRUDUser(User)
