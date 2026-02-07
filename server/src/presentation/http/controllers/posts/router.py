from fastapi import APIRouter

from src.presentation.http.controllers.posts.create_post import create_create_post_router
from src.presentation.http.controllers.posts.delete_post import create_delete_post_router
from src.presentation.http.controllers.posts.edit_post import create_edit_post_router
from src.presentation.http.controllers.posts.get_post import create_get_post_by_id_router
from src.presentation.http.controllers.posts.list_posts import create_list_posts_router
from src.presentation.http.controllers.posts.publish_post import create_publish_post_router


def create_posts_router() -> APIRouter:
    router = APIRouter(
        prefix="/posts",
        tags=["Posts"],
    )
    router.include_router(create_create_post_router())
    router.include_router(create_publish_post_router())
    router.include_router(create_delete_post_router())
    router.include_router(create_edit_post_router())
    router.include_router(create_list_posts_router())
    router.include_router(create_get_post_by_id_router())
    return router
