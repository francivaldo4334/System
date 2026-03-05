from django.contrib import admin
from stock.models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(PriceHistory)
admin.site.register(StockLocation)
# admin.site.register(StockMovement)

@admin.register(
    Purchase,
    Sale,
    Scrap,
    StockLoss,
    StockGain,
)
class StockMovimentFixed(admin.ModelAdmin):
    exclude = ['origin', 'destination']
