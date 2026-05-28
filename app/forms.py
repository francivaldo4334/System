from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, List

from django import forms
from authentication.models import CustomUser
from authentication.services import SendEmail

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
    url_query_params: str = "";
    type:str = "select"

@dataclass
class NumberField(Field):
    type:str = 'number'

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

class BaseForm:
    key:str
    form_fields: List[Field] = []
    def __init__(self) -> None:
        self._form = Form(
            fields=self.form_fields
        );
    @property
    def fields(self):
        return self._form.fields

# forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
class AvailabilityForm(BaseForm):
    key = 'availability'
    form_fields = [
        DateField(
            name="valid_from",
            label=_("Valid From"),
            attrs="required",
            value=timezone.localtime(timezone.now()).date().isoformat(),
        ),
        DateField(
            name="valid_until",
            label=_("Valid Until"),
            attrs="required",
            value=timezone.localtime(timezone.now() + timedelta(days=90)).date().isoformat(),
        ),
        CheckboxesField(
            name="week",
            label=_("Weekdays"),
            options=[
                CheckboxesField.Option(value="0", label=_("Mon"), attrs="checked"),
                CheckboxesField.Option(value="1", label=_("Tue"), attrs="checked" ),
                CheckboxesField.Option(value="2", label=_("Wed"), attrs="checked" ),
                CheckboxesField.Option(value="3", label=_("Thu"), attrs="checked" ),
                CheckboxesField.Option(value="4", label=_("Fri"), attrs="checked" ),
                CheckboxesField.Option(value="5", label=_("Sat") ),
                CheckboxesField.Option(value="6", label=_("Sun") ),
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
            label=_("Description"),
            attrs='required'
        )
    ]

class ResourceForm(BaseForm):
    key = 'resources'
    form_fields = [
        Field(
            name="name",
            label=_('Name'),
            attrs="required",
        ),
    ]
class ResourcePersonForm(BaseForm):
    key = 'resources'
    form_fields = [
        Field(
            name="username",
            label=_('Username'),
            attrs="required",
        ),
    ]

class AssignmentForm(BaseForm):
    key = 'assignment'
    form_fields = [
        SelectField(
            label=_('Service'),
            name="service",
            url_name="services",
        ),
        SelectField(
            label=_('Resources'),
            name="resources",
            url_name="resources",
            url_query_params='?is_selectable=true',
            attrs="multiple",
        ),
        NumberField(
            label='',
            name='availability',
            attrs='hidden'
        ),
        NumberField(
            label='',
            name='start_slot',
            attrs='hidden'
        ),
        DateField(
            label='',
            name='date',
            attrs='hidden'
        ),
    ]

class ServiceForm(BaseForm):
    key = 'services'
    form_fields = [
        Field(
            name="label",
            label=_('Name'),
            attrs="required",
        ),
        TextareaField(
            name="description",
            label=_('Description'),
            attrs="required",
        ),
        SelectField(
            label=_('Resource Types'),
            name="required_resources",
            url_name="resources",
            url_query_params='?use_as_category=true',
            attrs="multiple",
        ),
    ]

class UserForm(BaseForm):
    key = 'users'
    
    form_fields = [
        Field(
            name="username",
            label=_('User Name'),
            attrs="required",
        ),
        Field(
            name="first_name",
            label=_('First Name'),
            attrs="required",
        ),
        Field(
            name="last_name",
            label=_('Last Name'),
            attrs="required",
        ),
        Field(
            name="email",
            label=_('Email'),
            attrs="required type='email'",
        ),
        Field(
            name="password",
            label=_('Password'),
            attrs="type='password'",
        ),
    ]    

class ServiceRequirementsForm(BaseForm):
    key = 'service_requirements'
    form_fields = [
        SelectField(
            name='service',
            url_name='services',
            label=_('Service'),
            attrs='required'
        ),
        SelectField(
            name='resource_type',
            url_name='resources',
            label=_('Resource Type'),
            url_query_params='?use_as_category=true',
            attrs='required'
        ),
        # NumberField(
        #     name='quantity',
        #     label=_('Quantity'),
        #     attrs='required min="1" step="1"'
        # )
        
    ]
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        # Remove o request dos kwargs para não quebrar o formulário base
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit)
        SendEmail().send_email_cofirmation(user, self.request)
        return user
