from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, ServicePriceViewSet, LinkViewSet

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'service-prices', ServicePriceViewSet)
router.register(r'links', LinkViewSet)

urlpatterns = router.urls
