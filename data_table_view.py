from textual.widgets import DataTable

from rich.text import Text


class DataTableView(DataTable):

    def __init__(self, documents=None, **kwargs):
        super().__init__(**kwargs)
        if documents is None:
            self.documents = []
        else:
            self.documents = documents
        self.selected_docs = []

    def on_mount(self) -> None:
        self.add_column("本別", width=4, key="doc_type")
        self.add_column("來文日期", width=10, key="issue_date")
        self.add_column("限辦日期", width=10, key="deadline")
        self.add_column("來文字號", width=20, key="external_doc_number")
        self.add_column("公文文號", width=12, key="internal_doc_number")
        self.add_column(Text("主旨", justify="center"), width=50, key="title")
        self.add_column("來文單位", width=20, key="issue_unit")
        self.load_documents()
        self.focus()

    def load_documents(self):
        for number, d in enumerate(self.documents, start=1):
            row_data = (d.doc_type, d.issue_date, d.deadline, d.external_doc_number, d.internal_doc_number, d.title,
                        d.issue_unit)
            if (number - 1, d.doc_id) in self.selected_docs:
                row_data = (Text(s, style="grey89 on steel_blue") for s in row_data)

            self.add_row(
                *row_data, label=str(number), height=None, key=d.doc_id)

    def on_data_table_row_selected(self, message: DataTable.RowSelected):

        row_key = message.row_key
        row_index = message.cursor_row

        selected_row_metadata = (row_index, row_key.value)

        if selected_row_metadata not in self.selected_docs:
            self.selected_docs.append(selected_row_metadata)

        else:
            self.selected_docs.remove(selected_row_metadata)

        self.reload_rows()
        self.move_cursor(row=row_index)

    def reload_rows(self):
        self.clear()
        self.load_documents()

    def unselect_all_document(self):
        self.selected_docs = []
        self.reload_rows()
