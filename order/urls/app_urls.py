from django.urls import path, include
from order.views.app_views import SOrderListAPIViews, SOrderDetailAPIView, \
    SOrderLinkCreateAPIView, STelegramBackfillAPIView

urlpatterns = [
    path('orders/', SOrderListAPIViews.as_view()),
    path('orders/<int:pk>/', SOrderDetailAPIView.as_view()),
    # path('create-with-links/', SOrderWithLinksChildCreateAPIView.as_view()),
    path('order-create-link/', SOrderLinkCreateAPIView.as_view()),
    path('order-posts-create/', STelegramBackfillAPIView.as_view()),
]
