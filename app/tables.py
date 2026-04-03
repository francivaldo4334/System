from dataclasses import dataclass
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
