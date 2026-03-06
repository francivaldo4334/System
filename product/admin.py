# pyright: reportIncompatibleMethodOverride=false
from django.contrib import admin
from product.models import Category, PriceHistory, Product, UnitType

# Register your models here.
admin.site.register(Category)
admin.site.register(PriceHistory)
admin.site.register(UnitType)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return ('code',) if obj else ()
