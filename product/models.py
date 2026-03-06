# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportArgumentType=false
from django.db import models
from stdnum.util import isdigits
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from stdnum import ean

# Create your models here.
class Category(TitleDescriptionModel):
    pass

class UnitType(ActivatorModel,
               TitleDescriptionModel):
    pass

class Product(ActivatorModel,
              TimeStampedModel,
              TitleDescriptionModel):
    class CodeType(models.IntegerChoices):
        EAN = 0, 'EAN type'
        INTERNAL = 1, 'Internal code'

        
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE, default=1)
    code_type = models.SmallIntegerField(choices=CodeType.choices, default=CodeType.EAN.value)
    code = models.CharField(max_length=30, unique=True, validators=[isdigits,ean.is_valid])
    categories = models.ManyToManyField(Category, related_name='products')

    class Meta:
        unique_together = ('title', 'unit_type')

    @property
    def last_id(self):
        return self.__class__.objects.aggregate( # type: ignore
            max_id=models.Max('id'),
        )['max_id'] or 0
        

    def generate_internal_code(self, sequential):
        base = f"20{str(sequential).zfill(10)}"
        return f"{base}{ean.calc_check_digit(base)}"

    def clean(self):
        if not self.pk and self.code_type == self.CodeType.INTERNAL.value:
            self.code = self.generate_internal_code(self.last_id + 1)
    
class UnitConversion(TimeStampedModel):
    product = models.ForeignKey(Product, models.CASCADE, 'conversions')
    from_unit = models.ForeignKey(UnitType, models.CASCADE, 'conversions_from')
    to_unit = models.ForeignKey(UnitType, models.CASCADE, 'conversions_to')
    factor = models.DecimalField(max_digits=10, decimal_places=3, default=1)

    class Meta:
        unique_together = ('product', 'from_unit', 'to_unit')

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
