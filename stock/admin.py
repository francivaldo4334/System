from django.contrib import admin
from stock.models import *

# Register your models here.
admin.site.register(StockLocation)
@admin.register(
    Purchase,
    Sale,
    Scrap,
    StockLoss,
    StockGain,
)
class StockMovimentFixed(admin.ModelAdmin):
    exclude = ['origin', 'destination']
