# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportIncompatibleVariableOverride=false
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel
from django.core.validators import MinValueValidator, MaxValueValidator

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

class PriceHistory(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        related_name="price_history",
        on_delete=models.CASCADE,
    )
    cost_price = models.DecimalField(max_digits=20, decimal_places=2)
    target_margin = models.DecimalField(max_digits=5, decimal_places=2,validators=[MinValueValidator(0), MaxValueValidator(0.99)])
    price = models.GeneratedField(
        expression=models.F('cost_price') / (1 - (models.F('target_margin'))),
        output_field=models.DecimalField(max_digits=20, decimal_places=2),
        db_persist=True,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
    )
    class Meta:
        ordering = ['-created']


class StockLocation(ActivatorModel, TitleDescriptionModel):
    is_virtual = models.BooleanField(default=False)
    slug = models.SlugField()

class StockMovement(TimeStampedModel):
    product = models.ForeignKey(
        Product,
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
