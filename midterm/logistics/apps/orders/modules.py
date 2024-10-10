from injector import Module, Binder, singleton

from apps.orders.services import OrderService, OrderServiceImpl


class OrderModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(OrderService, to=OrderServiceImpl, scope=singleton)
