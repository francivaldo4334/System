# pyright: reportIncompatibleVariableOverride=false
from django.db import models
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

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
