from fastcrud import FastCRUD

from tests.fastapi.src.models.post import Post
from tests.fastapi.src.schemas.post import PostCreateInternal, PostDelete, PostUpdate, PostUpdateInternal


CRUDPost = FastCRUD[Post, PostCreateInternal, PostUpdate, PostUpdateInternal, PostDelete, None]
crud_posts = CRUDPost(Post)
