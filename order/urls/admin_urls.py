from django.urls import path, include
from rest_framework.routers import DefaultRouter

from service.views.app_views import SOrderWithLinksCreateView
from order.views.admin_views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-with-links/', SOrderWithLinksCreateView.as_view()),
]
