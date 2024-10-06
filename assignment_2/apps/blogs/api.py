from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ninja.responses import Response
from ninja_extra import route, ControllerBase, api_controller, paginate
from ninja_extra.pagination import PageNumberPaginationExtra
from ninja_extra.schemas import NinjaPaginationResponseSchema, PaginatedResponseSchema

from apps.blogs.models import Post
from apps.blogs.schemas import PostSchema, PostRetrieveSchema, PostCreateSchema, PostUpdateSchema, CommentSchema, \
    CommentCreateSchema, CommentSimpleSchema
from apps.blogs.services import get_posts, get_post_by_id, create_post, update_post, delete_post_by_id, create_comment, \
    get_comments, get_comments_by_post
from apps.users.permissions import IsBlogUser
from apps.utils.schemas import NoContentSchema


@api_controller('blog-posts/', tags=['blogs'], permissions=[IsBlogUser])
class BlogPostController(ControllerBase):
    @route.get('my/', response=PaginatedResponseSchema[PostSchema])
    @paginate()
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

    @route.get('{id}/comments/', response=PaginatedResponseSchema[CommentSimpleSchema])
    @paginate()
    def get_comments(self, id: int):
        comments = get_comments_by_post(id)
        return comments


@api_controller('blog-posts/comments/', tags=['comments'], permissions=[IsBlogUser])
class BlogCommentController(ControllerBase):

    @route.get('my/', response=PaginatedResponseSchema[CommentSchema])
    @paginate()
    def get_my_comments(self):
        user = self.context.request.auth
        comments = get_comments(user)
        return comments

    @route.post('', response=CommentSchema)
    def create_comment(self, payload: CommentCreateSchema):
        user = self.context.request.auth
        comment = create_comment(user, payload)
        return comment
