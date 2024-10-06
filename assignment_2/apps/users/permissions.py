from django.http import HttpRequest
from ninja_extra.permissions import IsAuthenticated


class IsBlogUser(IsAuthenticated):

    def has_permission(
            self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        return hasattr(request.auth, 'blog_user')
