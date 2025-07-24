from django.urls import path
from balance.views.app_views import SBalanceMeAPIView, \
    STransferListCreateAPIView, SGiftActivateAPIView, SBuyListAPIView, SOrderBuyListAPIView, SGiftUsageAPIView

urlpatterns = [
    # path('add/update/', SBalanceAddUpdateAPIView.as_view(), name='balance-add-update'),
    # path('subtraction/update/', SBalanceSubtractionUpdateAPIView.as_view(), name='balance-subtraction-update'),
    path('me/', SBalanceMeAPIView.as_view(), name='balance-me'),

    path('transfers/', STransferListCreateAPIView.as_view(), name='transfer-list-create'),

    path('gift/activate/', SGiftActivateAPIView.as_view(), name='gift-activate'),
    path('buy/list/', SBuyListAPIView.as_view(), name='buy-list'),
    path('order-buy/list/', SOrderBuyListAPIView.as_view(), name='order-buy-list'),
    path('gift-usage/', SGiftUsageAPIView.as_view(), name='gift-usage'),

]
