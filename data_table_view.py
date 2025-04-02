from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable

from rich.text import Text

class DataTableView(Container):

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("來文日期",width=15,key="date")
        table.add_column("公文文號", width=15, key="serial_no")
        table.add_column(Text("主旨",justify="center"), width=50, key="subject")
        table.add_column("來文單位", width=20, key="depart")
        table.add_column("辦理情形", width=10, key="stats")