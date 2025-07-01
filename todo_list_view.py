from textual.widgets import DataTable
from rich.text import Text
import json

class TodoListView(DataTable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todos = []
        self.selected_todos = []

    def on_mount(self) -> None:
        self.add_column("事項", width=50, key="task")
        self.add_column("期限", width=20, key="deadline")
        self.add_column("狀態", width=10, key="status")
        self.load_todos()
        self.focus()

    def load_todos(self):
        try:
            with open("todos.json", "r", encoding="utf-8") as f:
                self.todos = json.load(f)
        except FileNotFoundError:
            self.todos = []
        
        self.clear()
        for todo in self.todos:
            self.add_row(todo["task"], todo["deadline"], todo["status"], key=todo["id"])

    def on_data_table_row_selected(self, message: DataTable.RowSelected):
        row_key = message.row_key.value

        if row_key in self.selected_todos:
            self.selected_todos.remove(row_key)
        else:
            self.selected_todos.append(row_key)

        self.load_todos()
