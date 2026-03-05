# pyright: reportIncompatibleMethodOverride=false
from django.contrib import admin
from stock.models import *

# Register your models here.
admin.site.register(StockLocation)
admin.site.register(StockBalance)
@admin.register(
    Purchase,
    Sale,
    Scrap,
    StockLoss,
    StockGain,
)
class StockMovimentFixed(admin.ModelAdmin):
    exclude = ['origin', 'destination']
    def get_readonly_fields(self, request, obj=None):
        return ('product', 'quantity', 'reason', 'origin', 'destination') if obj else ()
