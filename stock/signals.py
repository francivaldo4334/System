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
            if not instance.origin.is_virtual:
                source_item, _ = StockBalance.objects.get_or_create(
                    product=instance.product,
                    location=instance.origin,
                )
                source_item.quantity -= instance.quantity
                source_item.save()
            if not instance.destination.is_virtual:
                dest_item, _ = StockBalance.objects.get_or_create(
                    product=instance.product,
                    location=instance.destination,
                )
                dest_item.quantity += instance.quantity
                dest_item.save()
