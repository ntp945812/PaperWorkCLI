from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable
from document import Document
from typing import List

from rich.text import Text

class DataTableView(Container):

    def __init__(self, papers: List[Document]):
        super().__init__()
        self.papers = papers

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("本",width=2, key="stats")
        table.add_column("來文日期",width=10,key="send_date")
        table.add_column("來文字號", width=20, key="send_no")
        table.add_column("公文文號", width=12, key="serial_no")
        table.add_column(Text("主旨",justify="center"), width=70, key="subject")
        table.add_column("來文單位", width=20, key="send_depart")
        table.add_column("限辦日期", width=10, key="deline")
        self.add_data_rows()

    def add_data_rows(self):
        table = self.query_one(DataTable)
        data = [(p.doc_type, p.issue_date, p.external_doc_number, p.internal_doc_number, p.title, p.issue_unit, p.deadline) for p in self.papers]
        for d in data:
            table.add_row(*d, height=None)