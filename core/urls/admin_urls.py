from django.urls import path, include

urlpatterns = [
    path('users/', include("users.urls.admin_urls")),
    path('services/', include("service.urls.admin_urls")),
    path('orders/', include("order.urls.admin_urls")),
    path('balances/', include("balance.urls.admin_urls")),
    path('notification/', include("notification.urls.admin_urls")),
]