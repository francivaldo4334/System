from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _
from typing import Any, List, Tuple
@dataclass
class HeaderOption:
    label:Any
@dataclass
class Header:
    options:List[HeaderOption]

@dataclass
class RowDataOption:
    key:str
    type:str
@dataclass
class RowData:
    options:List[RowDataOption]

    def get_object_data(self):
        return {opt.key:opt.type for opt in self.options}

@dataclass
class Table:
    list_url_name: str
    header:Header
    row_data:RowData

class BaseTable:
    key: str
    thead: list
    tr: List[Tuple[str, str]]

    def __init__(self) -> None:
        self._table = Table(
            list_url_name=f'{self.key}-list',
            header=Header(
                options=[HeaderOption(label=it) for it in self.thead]
            ),
            row_data=RowData(
                options=[RowDataOption(
                    key=key,
                    type=type
                ) for key, type in self.tr]
            )
        )

    @property
    def list_url_name(self):
        return self._table.list_url_name;

    @property
    def header(self):
        return self._table.header;

    @property
    def row_data(self):
        return self._table.row_data;
# tables
class AvailabilityTable(BaseTable):
    key = 'availabilities'
    thead = [
        _("Valid From"),
        _("Valid Until"),
        _("Description"),
    ]
    tr = [
        ('valid_from', 'date'),
        ('valid_until', 'date'),
        ('description', 'text'),
    ]
class ResourcesTable(BaseTable):
    key = 'resources'
    thead = [
        _('Resource Name'),
        _('Is Selectable'),
        _('Resource Type'),
    ]
    tr = [
        ('label', 'text'),
        ('is_selectable', 'checked'),
        ('parent_label', 'text'),
    ]
