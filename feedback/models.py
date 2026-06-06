from django.db import models
from core.models import CreatedByModel, TimeStampedModel

# Create your models here.
class Notification(TimeStampedModel, CreatedByModel):
    text = models.TextField()
    class Meta:
        abstract = True

class Message(Notification):
    class Category(models.TextChoices):
        BUG = 'BG', "Bug / Problema"
        FEATURE = "FT", "Sugestão / Novo Recurso"
        OUTHER = "OT", "Elogio / Outros"

    class Status(models.TextChoices):
        NEW = "NW","Novo"
        REVIEW = "RV","Em analise"
        COMPLECTED = "CP","Concluido"

    category = models.CharField(
        choices=Category.choices,
        max_length=2,
    )
    status = models.CharField(
        choices=Status.choices,
        max_length=2,
        default=Status.NEW.value,
    )

class Response(Notification):
    feedback = models.ForeignKey(Message, models.CASCADE)
