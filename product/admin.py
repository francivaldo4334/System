from django.contrib import admin
from product.models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(PriceHistory)

@admin.register(Product)
class Product(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return ('code',) if obj else ()
