from django.http import HttpRequest
from ninja_extra.permissions import IsAuthenticated


class IsMobileUser(IsAuthenticated):

    def has_permission(
            self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        return hasattr(request.auth, 'mobile_user')


class IsWebUser(IsAuthenticated):
    def has_permission(
            self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        return hasattr(request.auth, 'web_user')