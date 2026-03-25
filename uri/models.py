from django.db import models
from django.core.validators import RegexValidator
from django.db.models.functions import Concat

# Create your models here.
class URIModel(models.Model):
    app_label = models.CharField(validators=[RegexValidator(r"^[a-z_]+\Z")])
    model_name = models.CharField(validators=[RegexValidator(r"^[a-z_]+\Z")])
    target_id = models.CharField(validators=[RegexValidator(r"^[0-9a-z_:]+\Z")])
    uri = models.GeneratedField(
        expression=Concat(
            models.Value("uri:"),
            "app_label",
            models.Value(":"),
            "model_name",
            models.Value(":"),
            "target_id"
        ),
        output_field=models.CharField(max_length=500),
        db_persist=True,
    )
    class Meta:
        indexes = [
            models.Index(fields=['uri'])
        ]
        unique_together = ['app_label', 'model_name', 'target_id']
