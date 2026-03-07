# pyright: reportIncompatibleVariableOverride=false
# pyright: reportAssignmentType=false
# pyright: reportArgumentType=false
import uuid
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from core.models import CreatedByModel, TimeStampedModel

# Create your models here.
class Account(TimeStampedModel):
    name = models.CharField()
    code = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^\d+(\.\d+)*$')])
    is_selectable = models.BooleanField(default=True)
    parent = models.ForeignKey('self',models.CASCADE,'children', null=True, blank=True)

class AccountSelectable(Account):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_selectable=True)

    objects = Manager()

    class Meta:
        proxy = True


class Transaction(TimeStampedModel,
                  CreatedByModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reason = models.TextField(validators=[MinLengthValidator(3)])
    date = models.DateTimeField()

    @property
    def balance(self):
        return self.entries.all( # type: ignore
        ).aggregate(
            balance=models.Sum(
                models.Case(
                    models.When(entry_type=JournalEntry.Type.DEBIT.value, then='amount'),
                    models.When(entry_type=JournalEntry.Type.CREDIT.value, then=-models.F('amount')),
                    default=models.Value(0)
                )
            )
        )['balance'] or 0

    def is_balanced(self):
        return self.balance == 0

class JournalEntry(models.Model):
    class Type(models.TextChoices):
        DEBIT = 'D', 'Débito'
        CREDIT = 'C', 'Crédito'

    entry_type = models.CharField(max_length=1, choices=Type.choices)
    transaction = models.ForeignKey(Transaction,models.CASCADE,'entries')
    account = models.ForeignKey(AccountSelectable,models.PROTECT)
    amount = models.DecimalField(max_digits=20,
                                 decimal_places=2,
                                 validators=[MinValueValidator(0.01)])

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='amount_must_be_positive'
            )
        ]
