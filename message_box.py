from textual.app import ComposeResult
from textual.containers import Container, Center
from textual.widgets import Label

class MessageBox(Container):

    def compose(self) -> ComposeResult:
        yield Center(Label("Message Box"))
