from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .api import urlpatterns as api_urls
from .ssr import urlpatterns as ssr_urls

# 1. Rotas base (API e SSR)
urlpatterns = api_urls + ssr_urls

# 2. Rotas exclusivas de Desenvolvimento / Debug
if settings.DEBUG:
    docs_urls = [
        path("__reload__/", include("django_browser_reload.urls")),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
    
    urlpatterns += docs_urls
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
