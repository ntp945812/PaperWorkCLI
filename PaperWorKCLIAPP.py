from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Button, Input

from login_view import LoginView
from webWorker import WebWorker
from data_table_view import DataTableView

class PaperWorkCLIApp(App):
    """A Textual app to manage stopwatches."""
    def __init__(self):
        super().__init__()
        self.web_worker = WebWorker()

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "paper-work.tcss"


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield LoginView(web_worker=self.web_worker)
        yield Footer()


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "login_button":
            user_id = self.query_one("#userID", Input).value
            user_pwd = self.query_one("#userPWD", Input).value
            user_rnd = self.query_one("#userRnd", Input).value

            self.web_worker.login(user_id, user_pwd, user_rnd)

            if self.web_worker.is_login:
                self.query_one(LoginView).remove()
                self.mount(DataTableView(self.web_worker.get_all_docs()))


if __name__ == "__main__":
    app = PaperWorkCLIApp()
    app.run()