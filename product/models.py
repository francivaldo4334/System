# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportArgumentType=false
from django.db import models
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from stdnum import ean

# Create your models here.
def generate_internal_code(sequential):
    base = f"20{str(sequential).zfill(10)}"
    digits = [int(d) for d in base]
    total = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits))
    verifier = (10 - (total % 10)) % 10
    return f"{base}{verifier}"

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
    class CodeType(models.IntegerChoices):
        EAN = 0, 'EAN type'
        INTERNAL = 1, 'Internal code'

        
    code_type = models.SmallIntegerField(choices=CodeType.choices, default=CodeType.EAN.value)
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
    def clean(self):
        if self.code_type == self.CodeType.EAN and not ean.is_valid(self.code):
            raise ValidationError({'code': _('Enter a valid value.')})

        if not self.pk and self.code_type == self.CodeType.INTERNAL.value:
            last_product = self.__class__.objects.select_for_update().order_by('-id').first() # type: ignore            
            last_id = last_product.id if last_product else 0
            self.code = generate_internal_code(last_id + 1)

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
