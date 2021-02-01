from injector import singleton

from Synchronization.order_request_service import OrderRequestService
from Synchronization.synchronization_service import SynchronizationService
from Synchronization.schedule_service import ScheduleService
from account.account_service import AccountService
from order.options_fabric import OptionsFabric, OptionsFabricImpl
from order.order_service import OrderService


def configure(binder):

    binder.bind(OrderService, to=OrderService, scope=singleton)
    binder.bind(SynchronizationService, to=SynchronizationService, scope=singleton)
    binder.bind(ScheduleService, to=ScheduleService, scope=singleton)
    binder.bind(OrderRequestService, to=OrderRequestService, scope=singleton)
    binder.bind(OptionsFabric, to=OptionsFabricImpl, scope=singleton)
    binder.bind(AccountService, to=AccountService, scope=singleton)