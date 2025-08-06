from django.urls import path
from payment.views.app_views import PaymentEncodeAPIView, CheckOderBuyAPIView, PaymentPaidAPIView

urlpatterns = [
    path('encode/<int:buy_id>', PaymentEncodeAPIView.as_view()),
    path('check-user/', CheckOderBuyAPIView.as_view()),
    path('paid/', PaymentPaidAPIView.as_view()),
]
