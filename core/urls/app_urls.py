from django.urls import path, include

urlpatterns = [
    path('users/', include("users.urls.app_urls")),
    path('services/', include("service.urls.app_urls")),
    path('orders/', include("order.urls.app_urls")),
    path('balances/', include("balance.urls.app_urls")),
    path('notification/', include("notification.urls.app_urls")),
    path('payment/', include("payment.urls.app_urls")),
]
