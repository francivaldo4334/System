# pyright: reportAttributeAccessIssue=false
# pyright: reportGeneralTypeIssues=false
from typing import Any, Protocol
from django.db import transaction
from django.db.models.base import post_save
from django.dispatch import receiver
from stock.models import StockBalance, StockLocation, StockMovement

class TypeStockMovement(Protocol):
    origin: StockLocation
    destination: StockLocation
    quantity: int
    product: Any

@receiver(post_save, sender=StockMovement)
def update_stock_balance(sender, instance: TypeStockMovement, created, **kwargs):
    if created:
        with transaction.atomic():
            source_item, _ = StockBalance.objects.get_or_create(
                product=instance.product,
                location=instance.origin,
            )
            dest_item, _ = StockBalance.objects.get_or_create(
                product=instance.product,
                location=instance.destination,
            )

            source_item.quantity -= instance.quantity
            dest_item.quantity += instance.quantity

            source_item.save()
            dest_item.save()
