from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Input, Button

class AddTodoView(VerticalGroup):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="事項", id="task_input")
        yield Input(placeholder="期限", id="deadline_input")
        yield Button("新增", variant="primary", id="confirm_add_todo_button")

