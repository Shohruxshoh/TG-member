from rest_framework.routers import DefaultRouter
from service.views.admin_views import CountryViewSet, ServiceViewSet, LinkViewSet

router = DefaultRouter()
router.register(r'countries', CountryViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'links', LinkViewSet)

urlpatterns = router.urls
