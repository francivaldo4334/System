# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportGeneralTypeIssues=false
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from core.models import ActivatorModel, TimeStampedModel, TitleDescriptionModel
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from stdnum.util import isdigits
from stdnum import ean

# Create your models here. 
class Category(TitleDescriptionModel):
    pass

class UnitType(ActivatorModel, TitleDescriptionModel):
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
    product = models.ForeignKey(Product,models.PROTECT,'movements')
    origin = models.ForeignKey(StockLocation,models.PROTECT,'outgoing_movements')
    destination = models.ForeignKey(StockLocation,models.PROTECT,'incoming_movements')
    reason = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, 
                                   decimal_places=3,
                                   validators=[MinValueValidator(0.001)])

    def save(self, *args, **kwargs):
        if self.pk: return
        with transaction.atomic():
            super().save(*args, **kwargs)
            if not self.origin.is_virtual:
                obj_orig, _ = StockBalance.objects.get_or_create(
                    product=self.product,
                    location=self.origin
                )
                StockBalance.objects.select_for_update().filter(pk=obj_orig.pk).update(
                    quantity=models.F('quantity') - self.quantity
                )

            if not self.destination.is_virtual:
                obj_dest, _ = StockBalance.objects.get_or_create(
                    product=self.product, 
                    location=self.destination
                )
                StockBalance.objects.select_for_update().filter(pk=obj_dest.pk).update(
                    quantity=models.F('quantity') + self.quantity
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    location = models.ForeignKey(StockLocation, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=3, default=0, validators=[MinValueValidator(0.001)])

    class Meta:
        unique_together = ('product', 'location')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name='quantity_gte_0',
                violation_error_message=_("This specific stock move already exists.")
            )
        ]
