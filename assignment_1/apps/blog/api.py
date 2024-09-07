from ninja.responses import Response
from ninja_extra import route
from ninja_extra.controllers.base import ControllerBase, api_controller

from apps.users.permissions import IsBlogUser


@api_controller('blog/', tags=['blogs'], permissions=[IsBlogUser])
class BlogController(ControllerBase):

    @route.get("hello/")
    def hello(self):
        return Response("Hello, Blog!")
