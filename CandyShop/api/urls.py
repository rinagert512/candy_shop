from django.urls import path, include
from .views import *


urlpatterns = [
    path("couriers", CouriersView.as_view()),
    path("couriers/<int:pk>", CourierView.as_view()),
    path("orders", OrdersView.as_view()),
    path("orders/assign", OrdersAssignView.as_view()),
    path("orders/complete", OrdersCompleteView.as_view()),
]