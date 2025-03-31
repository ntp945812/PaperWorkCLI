from rich.text import Text
from rich.style import Style
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable
from login_view import LoginView

class PaperWorkCLIApp(App):
    """A Textual app to manage stopwatches."""
    def __init__(self):
        super().__init__()

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "paper-work.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield DataTable(cursor_type="row")
        yield LoginView()
        yield Footer()


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("來文日期",width=15,key="date")
        table.add_column("公文文號", width=15, key="serial_no")
        table.add_column(Text("主旨",justify="center"), width=50, key="subject")
        table.add_column("來文單位", width=20, key="depart")
        table.add_column("辦理情形", width=10, key="stats")


if __name__ == "__main__":
    app = PaperWorkCLIApp()
    app.run()