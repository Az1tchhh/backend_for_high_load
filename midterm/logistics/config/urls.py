"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from typing import Union

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from apps.country.api import CountryController, CityController
from apps.orders.api import OrderController
from apps.paybox.api import PayboxController, PayboxResultController
from apps.pickup_point.api import PickUpPointController
from apps.users.avatars.api import AvatarController
from apps.users.personal_info.api import MyAddressController, PersonalInfoController
from apps.wallets.api import WalletController, TransactionController
from apps.warehouse.api import WarehouseController
from config import settings
from apps.users.api import MobileAuthenticationController, WebAuthenticationController, MobileUserController, \
    WebUserController
from apps.users.authorization import GlobalAuth
from config import settings

api = NinjaExtraAPI(auth=GlobalAuth())

# api.add_router("users/", 'apps.users.api.router')
# api.add_router("order/shipping-address", 'apps.orders.views.shipping_address_view.router', tags=['shipping-address'])

api.register_controllers(MobileAuthenticationController)
api.register_controllers(AvatarController)
api.register_controllers(WebAuthenticationController)
api.register_controllers(MobileUserController)
api.register_controllers(WebUserController)
api.register_controllers(PayboxController)
api.register_controllers(PayboxResultController)
api.register_controllers(CountryController)
api.register_controllers(CityController)
api.register_controllers(WarehouseController)
api.register_controllers(OrderController)
api.register_controllers(PickUpPointController)
api.register_controllers(MyAddressController)
api.register_controllers(PersonalInfoController)
api.register_controllers(WalletController)
api.register_controllers(TransactionController)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
