from django.urls import path, include
from rest_framework import routers
from stock import views

router = routers.DefaultRouter()

router.register(r'categories', views.CategoryViewSet)
router.register(r'unittypes', views.UnitTypeViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls))
]
