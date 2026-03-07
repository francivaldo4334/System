# pyright: reportAttributeAccessIssue=false
from rest_framework import viewsets

from stock.models import Category, Product, UnitType
from stock.serializers import CategorySerializer, ProductSerializer, UnitTypeSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UnitTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
