from textual.containers import Container

class MessageBox(Container):

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row")
