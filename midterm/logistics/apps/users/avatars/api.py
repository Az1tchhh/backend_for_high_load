from ninja import Form, UploadedFile, File
from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import AllowAny
from django.utils.translation import gettext_lazy as _
from apps.users.avatars.models import Avatar
from apps.users.avatars.schemas import AvatarSchema, AvatarCreateSchema, AvatarUpdateSchema
from apps.users.avatars.services import update_avatar, create_avatar
from apps.users.permissions import IsMobileUser
from apps.utils.schemas import NoContentSchema


@api_controller('avatar/', tags=['mobile-avatar'], permissions=[AllowAny])
class AvatarController(ControllerBase):

    @route.get('', response=list[AvatarSchema])
    def avatars(self):
        avatars = Avatar.objects.all()
        return avatars

    @route.post('', response=AvatarSchema)
    def create_avatar(self, payload: AvatarCreateSchema = Form(...), image: UploadedFile = File(...)):
        data = payload.dict()
        avatar = create_avatar(data, image)
        return avatar

    @route.get('{id}/', response=AvatarSchema)
    def retrieve_avatar(self, id: int):
        avatar = Avatar.objects.get(id=id)
        return avatar

    @route.put('{id}/', response=AvatarSchema)
    def update_avatar(self, id: int, payload: AvatarUpdateSchema, image: UploadedFile = File(...)):
        data = payload.dict()
        avatar = update_avatar(id, data, image)
        return avatar

    @route.post('{id}/set/', permissions=[IsMobileUser])
    def set_avatar(self, id: int):
        avatar = Avatar.objects.get(id=id)
        user = self.context.request.auth
        mobile_user = user.mobile_user
        mobile_user.avatar = avatar
        mobile_user.save()
        return {"message": _("Avatar was saved.")}
