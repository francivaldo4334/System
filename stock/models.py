# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportIncompatibleVariableOverride=false
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel
from django.core.validators import MinValueValidator

# Create your models here.
class StockLocation(ActivatorModel, TitleDescriptionModel):
    is_virtual = models.BooleanField(default=False)
    slug = models.SlugField()

class StockMovement(TimeStampedModel):
    product = models.ForeignKey(
        'product.Product',
        related_name="movements",
        on_delete=models.PROTECT,
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.001)])
    reason = models.TextField(blank=True, null=True)
    origin = models.ForeignKey(
        StockLocation,
        related_name="outgoing_movements",
        on_delete=models.PROTECT,
    )
    destination = models.ForeignKey(
        StockLocation,
        related_name="incoming_movements",
        on_delete=models.PROTECT,
    )
class MovimentFixed(StockMovement):
    origin_slug = ''
    destination_slug = ''

    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(
                origin__slug=self.model.origin_slug,
                destination__slug=self.model.destination_slug,
            )
    objects = Manager()
    def save(self, *args, **kwargs):
        if not self.pk:
            self.origin = StockLocation.objects.get(slug=self.origin_slug) # type: ignore
            self.destination = StockLocation.objects.get(slug=self.destination_slug) # type: ignore
        return super().save(*args, **kwargs)
    class Meta:
        proxy = True

class Purchase(MovimentFixed):
    origin_slug = 'vendors'
    destination_slug = 'warehouse'

    class Meta:
        proxy = True

class Sale(MovimentFixed):
    origin_slug = 'warehouse'
    destination_slug = 'customers'

    class Meta:
        proxy = True

class Scrap(MovimentFixed):
    origin_slug = 'warehouse'
    destination_slug = 'scrap'

    class Meta:
        proxy = True

class StockLoss(MovimentFixed):
    origin_slug = 'warehouse'
    destination_slug = 'inventory-loss'

    class Meta:
        proxy = True

class StockGain(MovimentFixed):
    origin_slug = 'inventory-loss'
    destination_slug = 'warehouse'

    class Meta:
        proxy = True

class StockBalance(TimeStampedModel):
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=3, default=0)

    class Meta:
        unique_together = ('product', 'location')
