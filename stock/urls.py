from django.urls import path, include
from rest_framework import routers
from stock import api

router = routers.DefaultRouter()

router.register(r'categories', api.CategoryViewSet)
router.register(r'unittypes', api.UnitTypeViewSet)
router.register(r'products', api.ProductViewSet)
router.register(r'locations', api.StockLocationViewSet)

urlpatterns = [
    path('api/stock/', include(router.urls))
]
