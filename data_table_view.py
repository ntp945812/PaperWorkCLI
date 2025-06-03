from textual.widgets import DataTable

from rich.text import Text

class DataTableView(DataTable):

    def __init__(self, documents=None,**kwargs):
        super().__init__(**kwargs)
        if documents is None:
            self.documents = []
        else:
            self.documents = documents
        self.selected_docs = []

    def on_mount(self) -> None:
        self.add_column("本別", width=4, key="doc_type")
        self.add_column("來文日期", width=10, key="issue_date")
        self.add_column("來文字號", width=20, key="external_doc_number")
        self.add_column("公文文號", width=12, key="internal_doc_number")
        self.add_column(Text("主旨", justify="center"), width=50, key="title")
        self.add_column("來文單位", width=20, key="issue_unit")
        self.add_column("限辦日期", width=10, key="deadline")
        self.add_data_rows()
        self.focus()

    def add_data_rows(self):
        for number, d in enumerate(self.documents, start=1):
            self.add_row(
                *(d.doc_type, d.issue_date, d.external_doc_number, d.internal_doc_number, d.title, d.issue_unit,
                  d.deadline), label=str(number), height=None, key=d.doc_id)

    def on_data_table_row_selected(self, message: DataTable.RowSelected):

        row_key = message.row_key
        row_index = message.cursor_row
        data_table = message.data_table

        selected_row_metadata = (row_index, row_key.value)

        if selected_row_metadata not in self.selected_docs:
            self.selected_docs.append(selected_row_metadata)
            for col in data_table.columns:
                data_table.update_cell(row_key, col,
                                       Text(data_table.get_cell(row_key, col), style="grey89 on steel_blue"))
        else:
            self.selected_docs.remove(selected_row_metadata)
            for col in data_table.columns:
                data_table.update_cell(row_key, col, data_table.get_cell(row_key, col).plain)

    def refresh_rows(self):
        self.clear()

