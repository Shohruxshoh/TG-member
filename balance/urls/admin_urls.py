from django.urls import path
from balance.views.admin_views import BalanceAddUpdateAPIView, BalanceSubtractionUpdateAPIView, BalanceMeAPIView, \
    TransferListCreateAPIView, GiftActivateAPIView

urlpatterns = [
    path('add/update/', BalanceAddUpdateAPIView.as_view(), name='balance-add-update'),
    path('subtraction/update/', BalanceSubtractionUpdateAPIView.as_view(), name='balance-subtraction-update'),
    path('me/', BalanceMeAPIView.as_view(), name='balance-me'),

    path('transfers/', TransferListCreateAPIView.as_view(), name='transfer-list-create'),

    path('gift/activate/', GiftActivateAPIView.as_view(), name='gift-activate'),
]
