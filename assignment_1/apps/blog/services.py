from typing import Optional

from apps.blog.models import Post, Comment
from apps.blog.schemas import PostCreateSchema, PostUpdateSchema, CommentCreateSchema
from apps.users.models import User
from apps.utils.exceptions import ValidationException


def get_posts(user: Optional[User] = None):
    if user:
        posts = Post.objects.filter(author=user)
        return posts
    posts = Post.objects.all()
    return posts


def get_post_by_id(post_id):
    post = Post.objects.filter(pk=post_id).first()
    if post is None:
        raise ValidationException("Post does not exist")
    return post


def create_post(payload: PostCreateSchema, user: User):
    data = payload.model_dump()
    post = Post.objects.create(**data, author=user)
    return post


def update_post(post_id: int, payload: PostUpdateSchema, user: User):
    my_posts = get_posts(user)
    post = my_posts.filter(id=post_id).first()
    if post is None:
        raise ValidationException("Post does not exist")

    data = payload.model_dump(exclude_unset=True)
    for attr, value in data.items():
        setattr(post, attr, value)

    post.save()
    return post


def delete_post_by_id(post_id: int, user: User):
    my_posts = get_posts(user)
    post = my_posts.filter(id=post_id).first()
    if post is None:
        raise ValidationException("post does not exist")
    post.delete()
    return


def get_comments(user: User):
    if user:
        comments = Comment.objects.filter(author=user)
        return comments
    comments = Comment.objects.all()
    return comments


def get_comments_by_post(post_id: int):
    post = get_post_by_id(post_id)
    if post is None:
        raise ValidationException("Post does not exist")
    return post.comments.all()


def create_comment(user: User, payload: CommentCreateSchema):
    data = payload.model_dump()
    comment = Comment.objects.create(**data, author=user)
    return comment