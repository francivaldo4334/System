# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportIncompatibleVariableOverride=false
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel

# Create your models here.
class Category(TitleDescriptionModel):
    pass

class Product(ActivatorModel,
              TimeStampedModel,
              TitleDescriptionModel):
    # class UnitTypeChoices(models.TextChoices):
    #     UNIT = 0, 'Unit'
    #     KILOGRAM = 1, 'Kilogram'
    #     GRAM = 2, 'Gram'
    #     LITER = 3, 'Liter'
    #     MILLILITER = 4, 'Milliliter'

    # unit_type = models.IntegerField(
    #     choices = UnitTypeChoices.choices,
    #     default=UnitTypeChoices.UNIT.value,
    # )
    code = models.CharField(max_length=30, unique=True)
    categories = models.ManyToManyField(Category, related_name='products')

    @property
    def price(self):
        last = self.price_history.order_by('-created').first() # type: ignore
        return last.price if last is not None else 0

    @property
    def stock_quantity(self):
        return self.movements.aggregate( # type: ignore
            total=models.Sum('quantity')
        )['total'] or 0

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_title')
        ]

class ProductPriceHistory(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        related_name="price_history",
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )
    cost_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )

class ProductPriceCurrentPrice(ProductPriceHistory):
    class Meta:
        proxy = True
        ordering = ['-created']


class StockLocation(ActivatorModel, TitleDescriptionModel):
    is_virtual = models.BooleanField(default=False)

class StockMovement(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        related_name="movements",
        on_delete=models.PROTECT,
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    reason = models.TextField(blank=True, null=True)
    origin = models.ForeignKey(
        StockLocation,
        related_name="outgoing_movements",
        on_delete=models.PROTECT,
        null=True, 
        blank=True,
    )
    destination = models.ForeignKey(
        StockLocation,
        related_name="incoming_movements",
        on_delete=models.PROTECT,
        null=True, 
        blank=True,
    )
