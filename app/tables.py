class ReaderOption:
    label:str
class Reader:
    options:ReaderOption
class RowData:
    key:str
    type:str
class Table:
    list_url_name: str
    reader:Reader
    row_data:RowData


class AvailabilityTable(Table):
    ...
