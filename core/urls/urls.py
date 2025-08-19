"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('core.urls.admin_urls')),
    path('api/app/', include('core.urls.app_urls')),
    # path('silk/', include('silk.urls', namespace='silk')),

    # Spectacular schema views
    path(
        "schema/admin/",
        SpectacularAPIView.as_view(urlconf="core.urls.admin_urls"),
        name="admin-schema",
    ),
    path(
        "schema/app/",
        SpectacularAPIView.as_view(urlconf="core.urls.app_urls"),
        name="app-schema",
    ),
    # Swagger UI for each API group
    path(
        "swagger/admin/",
        SpectacularSwaggerView.as_view(url_name="admin-schema"),
        name="admin-swagger",
    ),
    path(
        "swagger/app/",
        SpectacularSwaggerView.as_view(url_name="app-schema"),
        name="aoo-swagger",
    ),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='app-schema'), name='redoc'),
]
if settings.DEBUG:
    urlpatterns += (
            static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
            static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
