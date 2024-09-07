from ninja.responses import Response
from ninja_extra import route, ControllerBase, api_controller

from apps.blog.models import Post
from apps.blog.schemas import PostSchema, PostRetrieveSchema, PostCreateSchema, PostUpdateSchema
from apps.blog.services import get_posts, get_post_by_id, create_post, update_post, delete_post_by_id
from apps.users.permissions import IsBlogUser
from apps.utils.schemas import NoContentSchema


@api_controller('blog-posts/', tags=['blogs'], permissions=[IsBlogUser])
class BlogPostController(ControllerBase):
    @route.get("hello/")
    def hello(self):
        return Response("Hello, Blog!")

    @route.get('my/', response=list[PostSchema])
    def get_my_posts(self):
        user = self.context.request.auth
        posts = get_posts(user)
        return posts

    @route.get('', response=list[PostSchema])
    def get_posts(self):
        posts = get_posts()
        return posts

    @route.get('{id}/', response=PostRetrieveSchema)
    def get_post(self, id):
        post = get_post_by_id(id)
        return post

    @route.post('', response=PostRetrieveSchema)
    def create_post(self, payload: PostCreateSchema):
        user = self.context.request.auth
        post = create_post(payload, user)
        return post

    @route.patch('{id}/', response=PostRetrieveSchema)
    def update_post(self, id: int, payload: PostUpdateSchema):
        user = self.context.request.auth
        post = update_post(id, payload, user)
        return post

    @route.delete('{id}/', response={204: NoContentSchema})
    def delete_post(self, id: int):
        user = self.context.request.auth
        delete_post_by_id(id, user)
        return
