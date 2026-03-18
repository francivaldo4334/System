from .api import urlpatterns as api_urls
from .ssr import urlpatterns as ssr_urls
urlpatterns = api_urls + ssr_urls
