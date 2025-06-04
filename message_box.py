from textual import events
from textual.app import ComposeResult
from textual.containers import Center
from textual.widgets import Label
from textual.reactive import reactive


class MessageBox(Center):
    hided = reactive(True)

    def __init__(self):
        super().__init__()
        self.add_class("hided")

    def compose(self) -> ComposeResult:
        yield Label()

    def watch_hided(self, hided) -> None:
        if hided:
            self.add_class('hided')
        else:
            self.remove_class('hided')

    def alert(self, message: str = '', hide_after: float = 0.0):
        self.hided = False
        self.query_one(Label).update(message)
        if hide_after > 0:
            self.set_timer(hide_after, self.hide)

    def hide(self):
        self.hided = True
        self.query_one(Label).update("")

    def on_click(self, event: events.Click) -> None:
        self.hide()
