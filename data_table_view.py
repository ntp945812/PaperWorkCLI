from selenium.webdriver.common.devtools.v132.dom import focus
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable
from document import Document
from typing import List

from rich.text import Text

class DataTableView(Container):

    def __init__(self, documents: List[Document]):
        super().__init__()
        self.documents = documents
        self.selected_docs = []

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("本別",width=4, key="doc_type")
        table.add_column("來文日期",width=10,key="issue_date")
        table.add_column("來文字號", width=20, key="external_doc_number")
        table.add_column("公文文號", width=12, key="internal_doc_number")
        table.add_column(Text("主旨",justify="center"), width=50, key="title")
        table.add_column("來文單位", width=20, key="issue_unit")
        table.add_column("限辦日期", width=10, key="deadline")
        self.add_data_rows()
        table.focus()

    def add_data_rows(self):
        table = self.query_one(DataTable)
        for number,d in enumerate(self.documents, start=1):
            table.add_row(*(d.doc_type, d.issue_date, d.external_doc_number, d.internal_doc_number, d.title, d.issue_unit, d.deadline),label=str(number), height=None, key=d.doc_id )

    def on_data_table_row_selected(self, message:DataTable.RowSelected):

        row_key = message.row_key
        row_index = message.cursor_row
        data_table = message.data_table

        selected_row_metadata = (row_index,row_key.value)


        if selected_row_metadata not in self.selected_docs:
            self.selected_docs.append(selected_row_metadata)
            for col in data_table.columns:
                data_table.update_cell(row_key,col,Text(data_table.get_cell(row_key,col),style="grey89 on steel_blue"))
        else:
            self.selected_docs.remove(selected_row_metadata)
            for col in data_table.columns:
                data_table.update_cell(row_key,col,data_table.get_cell(row_key,col).plain)