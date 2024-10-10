import jwt
from ninja.security import HttpBearer
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ninja.errors import HttpError
from apps.users.models import User


class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.NINJA_JWT['SIGNING_KEY'], algorithms=settings.NINJA_JWT['ALGORITHM'])

            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)

            if not user.is_active:
                raise HttpError(403, _('User account is disabled.'))

            return user

        except jwt.ExpiredSignatureError:
            raise HttpError(401, _('Token has expired.'))
        except jwt.InvalidTokenError:
            raise HttpError(401, _('Invalid token.'))
        except User.DoesNotExist:
            raise HttpError(401, _('User does not exist.'))
        except Exception as e:
            raise HttpError(500, _('An error occurred while decoding token.'))
