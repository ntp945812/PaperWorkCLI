from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input


class ReturnDocumentScreen(ModalScreen[str]):
    """Screen with a dialog to quit."""

    def __init__(self, doc_title: str):
        super().__init__()
        self.doc_title = doc_title

    def compose(self) -> ComposeResult:
        yield Grid(Label(self.doc_title, id="return_document_title_label"),
                   Input(placeholder="退文說明", id="return_document_reason_input"),
                   Button("取消", variant="error", id="cancel"),
                   Button("確定", variant="primary", id="confirm"), id="dialog")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            reason_input = self.query_one("#return_document_reason_input", Input)
            self.dismiss(reason_input.value)
        else:
            self.dismiss("")
