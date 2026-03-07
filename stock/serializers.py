from rest_framework import serializers

from stock.models import Category, Product, UnitType
from drf_spectacular.utils import extend_schema_field


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description']


class UnitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitType
        fields = ['id', 'title', 'description']


class ProductSerializer(serializers.ModelSerializer):
    unit_type = UnitTypeSerializer()
    categories = CategorySerializer(many=True)
    price = serializers.DecimalField(20,2)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'unit_type',
            'code_type',
            'code',
            'categories',
            'price',
        ]
