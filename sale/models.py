# pyright: reportIncompatibleVariableOverride=false
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from core.models import ActivatorModel, CreatedByModel, TimeStampedModel

# Create your models here.
class CashAccount(TimeStampedModel,
                  ActivatorModel,
                  CreatedByModel):
    name = models.CharField()
    slug = models.SlugField()

    @property
    def balance(self):
        total = JournalEntry.objects.filter( # type: ignore
                transaction__account=self
            ).aggregate(total=models.Sum('amount'))['total'] or 0
        return round(total, 2)
        


class Transaction(TimeStampedModel,
                  ActivatorModel,
                  CreatedByModel):

    reason = models.TextField(
        validators=[MinLengthValidator(3)]
    )

    account = models.ForeignKey(
        CashAccount,
        related_name="transactions",
        on_delete=models.PROTECT,
    )
    slug = models.SlugField()

    @property
    def amount(self):
        total = self.entries.aggregate( # type: ignore
            total=models.Sum('amount')
        )['total']
        return round(total, 2)


class TransactionPositive(Transaction):
    class Manager(models.Manager):
        def get_queryset(self):
            qs = super().get_queryset()
            return qs.filter(entries__amount__gte=0).distinct()

    objects = Manager()

    class Meta:
        proxy = True

class TransactionNegative(Transaction):
    class Manager(models.Manager):
        def get_queryset(self):
            qs = super().get_queryset()
            return qs.filter(entries__amount__lt=0).distinct()

    objects = Manager()

    class Meta:
        proxy = True

class JournalEntry(models.Model):
    reason = models.TextField("Motivo", blank=True, null=True)
    transaction = models.ForeignKey(
        Transaction,
        related_name="entries",
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
    )


class JournalEntryPositive(JournalEntry):

    def clean(self):
        if self.amount and self.amount < 0.01:
            msg = _("Ensure this value is greater than or equal to %(limit_value)s.") % { 'limit_value': 0.01 }
            raise ValidationError(msg)

    class Meta:
        proxy = True

class JournalEntryNegative(JournalEntryPositive):
    def clean(self):
        super().clean()

        if self.amount:
            self.amount = -abs(self.amount)

    class Meta:
        proxy = True
