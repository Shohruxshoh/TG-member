from django.urls import path, include
from rest_framework.routers import DefaultRouter

from service.views import OrderWithLinksCreateView
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-with-links/', OrderWithLinksCreateView.as_view()),
]
