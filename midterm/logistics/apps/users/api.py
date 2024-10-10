from django.contrib.auth import authenticate
from django.db import transaction, IntegrityError
from ninja import Router, UploadedFile, File
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import APIException
from ninja_jwt.controller import TokenObtainPairController
from django.utils.translation import gettext_lazy as _
from .models import MobileUser, User, WebUser, WebUserAssignment
from .permissions import IsMobileUser, IsWebUser
from .schemas import MobileUserCreateSchema, MobileUserSchema, MobileUserLoginSchema, WebUserCreateSchema, \
    WebUserSchema, WebUserLoginSchema, MobileUserUpdateSchema, UserPasswordUpdateSchema
from .services import get_tokens_for_user, change_password, update_mobile_user
from ..pickup_point.models import PickUpPoint
from ..utils.enums import RoleType
from ..utils.exceptions import ValidationException
from ..wallets.models import Wallet
from ..warehouse.models import Warehouse

router = Router()


@api_controller('mobile/', tags=['authentication'], auth=None)
class MobileAuthenticationController(TokenObtainPairController):
    @route.post('token/')
    def obtain_token(self, user_token: MobileUserLoginSchema):
        data = user_token.dict()
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(username=email, password=password)
        if user is None or not hasattr(user, 'mobile_user'):
            raise ValidationException(_("Incorrect input data. Try again."))

        claims = get_tokens_for_user(user)
        claims['email'] = user.username
        return claims

    @route.post('register/', response={201: MobileUserSchema, })
    @transaction.atomic()
    def mobile_register(self, payload: MobileUserCreateSchema):
        data = payload.dict()
        email = data.pop("email", None)
        password = data.pop("password", None)
        if not email or not password:
            raise ValidationException(_("Enter your email and password."))
        try:
            user = User.objects.create(
                username=email,
                password=password,
                is_mobile_user=True,
            )
        except:
            raise ValidationException(_("A user with this email already exists."))

        try:
            mobile_user = MobileUser.objects.create(
                user=user,
                **data
            )
        except IntegrityError:
            raise ValidationException(_("The phone number is already in use."))
        Wallet.objects.create(user=user, balance=0)
        user.set_password(payload.password)
        user.save()
        mobile_user.save()
        return mobile_user


@api_controller('mobile/', tags=['mobile'], permissions=[IsMobileUser])
class MobileUserController(ControllerBase):

    @route.get('me/', response=MobileUserSchema)
    def me(self):
        user = self.context.request.auth
        return user.mobile_user

    @route.patch('user/edit/', response=MobileUserSchema)
    def mobile_edit(self, payload: MobileUserUpdateSchema):
        data = payload.dict(exclude_unset=True)
        user = self.context.request.auth

        mobile_user = user.mobile_user
        update_mobile_user(mobile_user, data)

        return mobile_user

    @route.post('upload/profile-photo/', response=MobileUserSchema)
    def upload_profile_photo(self, profile_photo: UploadedFile = File(...)):
        user = self.context.request.auth
        mobile_user = user.mobile_user

        mobile_user.profile_photo.save(profile_photo.name, profile_photo)
        mobile_user.save()
        return mobile_user

    @route.put('password/edit/')
    def mobile_password_edit(self, payload: UserPasswordUpdateSchema):
        data = payload.dict()
        user = self.context.request.auth

        change_password(user, data)
        return {"message": _("Password updated successfully.")}


@api_controller('web/', tags=['authentication'], auth=None)
class WebAuthenticationController(TokenObtainPairController):
    @route.post('token/')
    def obtain_token(self, user_token: WebUserLoginSchema):
        data = user_token.dict()
        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None or not hasattr(user, 'web_user'):
            raise ValidationException(_("The input data is incorrect. Please try again."))

        claims = get_tokens_for_user(user)
        claims['username'] = user.username
        claims['role'] = user.web_user.role
        return claims

    @route.post('register/', response={201: WebUserSchema, })
    @transaction.atomic()
    def web_register(self, payload: WebUserCreateSchema):
        data = payload.dict()
        username = data.pop("username", None)
        password = data.pop("password", None)
        role = data.get("role")
        warehouse_id = data.pop("warehouse_id", None)
        pickup_point_id = data.pop("pickup_point_id", None)
        if not username or not password:
            raise APIException(_("Enter your login and password."))
        try:
            user = User.objects.create(
                username=username,
                password=password,
                is_web_user=True,
            )
            user.set_password(payload.password)
            user.save()
        except IntegrityError:
            raise ValidationException(_("A user with this login already exists."))
        try:
            web_user = WebUser.objects.create(
                user=user,
                **data
            )
        except IntegrityError:
            raise ValidationException(_("The phone number is already in use."))

        try:
            if role == RoleType.WAREHOUSE_MANAGER and warehouse_id:
                if not warehouse_id:
                    raise ValidationException(_('Provide a warehouse for an employee.'))
                warehouse = Warehouse.objects.get(id=warehouse_id)
                WebUserAssignment.objects.create(
                    web_user=web_user,
                    warehouse=warehouse,
                )
            elif role == RoleType.PUP_MANAGER and pickup_point_id:
                if not pickup_point_id:
                    raise ValidationException(_('Provide a pick-up point for the employee.'))
                pickup_point = PickUpPoint.objects.get(id=pickup_point_id)
                WebUserAssignment.objects.create(
                    web_user=web_user,
                    pickup_point=pickup_point,
                )
            elif role == RoleType.ADMIN:
                pass
            else:
                raise ValidationException(_("Incorrect data for user binding."))
        except Warehouse.DoesNotExist:
            raise ValidationException(_("The specified warehouse was not found."))
        except PickUpPoint.DoesNotExist:
            raise ValidationException(_("The specified pick-up point was not found."))

        return web_user


@api_controller('web/', tags=['web'], permissions=[IsWebUser])
class WebUserController(ControllerBase):

    @route.get('me/', response=WebUserSchema)
    def me(self):
        user = self.context.request.auth
        return user.web_user
