from django.urls import path

from order.apps import OrderConfig
from order.views import CreateOrderView

app_name = OrderConfig.name

urlpatterns = [
    path('order/create', CreateOrderView.as_view(), name='create_order')
]
