from django.urls import path
from service.views.app_views import SCountryListAPIView, SServiceListAPIView

urlpatterns = [
    path('countries/', SCountryListAPIView.as_view()),
    path('services/', SServiceListAPIView.as_view()),
    # path('links/', SLinkListAPIView.as_view()),
]
