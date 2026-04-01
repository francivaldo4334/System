from dataclasses import dataclass
from typing import Any, List
@dataclass
class HeaderOption:
    label:Any
@dataclass
class Header:
    options:List[HeaderOption]
@dataclass
class RowData:
    key:str
    type:str

@dataclass
class Table:
    list_url_name: str
    header:Header
    row_data:RowData
