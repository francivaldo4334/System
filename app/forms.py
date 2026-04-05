from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class Field:
    label: Any;
    name: str;
    id: str = field(init=False);
    attrs: str = "";
    type: str = "input";
    value:str = "";

    def __post_init__(self):
        self.id = f"id_{self.name}";
    
@dataclass
class SelectField(Field):
    url_name: str = "";
    type:str = "select"

@dataclass
class DateField(Field):
    type:str = "date"

@dataclass
class CheckboxesField(Field):
    @dataclass
    class Option:
        value:str;
        label:Any;
        attrs:str = "";
    type:str = "checkboxes";
    options: List[Option] = field(default_factory=list);

@dataclass
class TimeField(Field):
    type:str = "time"
    step:str = "300"

@dataclass
class TextareaField(Field):
    type:str = "textaria"

@dataclass
class Form:
    fields:List

# forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
class AvailabilityForm:
    key = "availability"
    post_url_name = ""
    @property
    def fields(self):
        return self._form.fields
    _form = Form(
        fields=[
            SelectField(
                name="resource",
                label=_("Resource"),
                url_name="resources",
                attrs="required",
            ),
            DateField(
                name="valid_from",
                label=_("Valid From"),
                attrs="required",
                value=timezone.localtime(timezone.now()).date().isoformat(),
            ),
            DateField(
                name="valid_until",
                label=_("Valid Until"),
            ),
            CheckboxesField(
                name="week",
                label=_("Weekdays"),
                options=[
                    CheckboxesField.Option(value="1", label=_("Mon"), attrs="checked"),
                    CheckboxesField.Option(value="2", label=_("Tue"), attrs="checked" ),
                    CheckboxesField.Option(value="3", label=_("Wed"), attrs="checked" ),
                    CheckboxesField.Option(value="4", label=_("Thu"), attrs="checked" ),
                    CheckboxesField.Option(value="5", label=_("Fri"), attrs="checked" ),
                    CheckboxesField.Option(value="6", label=_("Sat") ),
                    CheckboxesField.Option(value="7", label=_("Sun") ),
                ]
            ),
            TimeField(
                name="time_from",
                label=_("Time From"),
                attrs="required",
                value="08:00",
            ),
            TimeField(
                name="time_until",
                label=_("Time Until"),
                attrs="required",
                value="17:00",
            ),
            TimeField(
                name="duration",
                label=_("Duration"),
                attrs="required",
                value="00:30",
            ),
            TimeField(
                name="interval",
                label=_("Interval"),
                attrs="required",
                value="00:10",
            ),
            TextareaField(
                name="description",
                label=_("Description")
            )
        ]
    )
