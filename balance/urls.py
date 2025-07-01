from django.urls import path

from balance.views import BalanceAddUpdateAPIView, BalanceSubtractionUpdateAPIView, BalanceMeAPIView

urlpatterns = [
    path('add/update/', BalanceAddUpdateAPIView.as_view(), name='balance-add-update'),
    path('subtraction/update/', BalanceSubtractionUpdateAPIView.as_view(), name='balance-subtraction-update'),
    path('me/', BalanceMeAPIView.as_view(), name='balance-me'),
]
