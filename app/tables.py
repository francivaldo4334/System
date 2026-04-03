from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _
from typing import Any, List
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
# tables
AvailabilityTable = Table(
        list_url_name="availabilities-list",
        header=Header(
            options=[
                HeaderOption(label=_("Resource")),
                HeaderOption(label=_("Valid From")),
                HeaderOption(label=_("Valid Until")),
                HeaderOption(label=_("Description"))
            ]
        ),
        row_data=RowData(
            options=[
                RowDataOption(
                    key="resource_label",
                    type="text"
                ),
                RowDataOption(
                    key="valid_from",
                    type="date",
                ),
                RowDataOption(
                    key="valid_until",
                    type="date",
                ),
                RowDataOption(
                    key="description",
                    type="text",
                ),                        
            ]
        )
    )
