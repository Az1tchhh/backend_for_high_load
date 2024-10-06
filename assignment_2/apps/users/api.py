from django.contrib.auth import authenticate
from django.db import transaction, IntegrityError
from ninja_extra import api_controller, route
from ninja_jwt.controller import TokenObtainPairController

from apps.users.models import User, BlogUser
from apps.users.schemas import BlogUserLoginSchema, BlogUserSchema, BlogUserCreateSchema
from apps.users.services import get_tokens_for_user
from apps.utils.exceptions import ValidationException


@api_controller('auth/', tags=['authentication'], auth=None)
class BlogAuthenticationController(TokenObtainPairController):
    @route.post('token/')
    def obtain_token(self, user_token: BlogUserLoginSchema):
        data = user_token.dict()
        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None or not hasattr(user, 'blog_user'):
            raise ValidationException("Неправильно указаны входные данные. Попробуйте заново.")

        claims = get_tokens_for_user(user)
        claims['username'] = user.username
        return claims

    @route.post('register/', response={201: BlogUserSchema, })
    @transaction.atomic
    def mobile_register(self, payload: BlogUserCreateSchema):
        data = payload.dict()
        username = data.pop("username")
        password = data.pop("password")
        try:
            user = User.objects.create(
                username=username,
                password=password,
                is_blog_user=True,
            )
        except IntegrityError as e:
            raise ValidationException(f"Пользователь уже существует: {username}")

        try:
            blog_user = BlogUser.objects.create(
                user=user,
                **data
            )
        except IntegrityError:
            raise ValidationException("Номер телефона уже используется")
        user.set_password(payload.password)
        user.save()
        blog_user.save()
        return blog_user
