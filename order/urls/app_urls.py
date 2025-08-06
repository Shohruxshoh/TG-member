from django.urls import path, include
from order.views.app_views import SOrderListAPIViews, SOrderDetailAPIView, \
    SOrderLinkCreateAPIView, STelegramBackfillAPIView, SAddVipAPIView, SOrderLinkListAPIView, SCheckAddedChannelAPIView

urlpatterns = [
    path('orders/', SOrderListAPIViews.as_view()),
    path('channel-links/', SOrderLinkListAPIView.as_view()),
    path('orders/<int:pk>/', SOrderDetailAPIView.as_view()),
    # path('create-with-links/', SOrderWithLinksChildCreateAPIView.as_view()),
    path('order-create-link/', SOrderLinkCreateAPIView.as_view()),
    path('order-posts-create/', STelegramBackfillAPIView.as_view()),
    path('subscribe-channel/', SAddVipAPIView.as_view()),
    path('check-channel/', SCheckAddedChannelAPIView.as_view()),
]
