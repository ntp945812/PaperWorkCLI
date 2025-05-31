from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Button, Input

from login_view import LoginView
from webWorker import WebWorker
from data_table_view import DataTableView
from message_box import MessageBox

class PaperWorkCLIApp(App):
    """A Textual app to manage stopwatches."""
    def __init__(self):
        super().__init__()
        self.web_worker = WebWorker()

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "save_doc", "Save document")
    ]
    CSS_PATH = "paper-work.tcss"

    def on_mount(self) -> None:
        self.theme = "gruvbox"


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield LoginView(web_worker=self.web_worker)
        yield MessageBox()
        yield Footer()


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "catppuccin-mocha" if self.theme == "gruvbox" else "gruvbox"
        )

    def action_save_doc(self) -> None:
        """Save selected document to unzip and merge"""
        selected_docs = self.query_one(DataTableView).selected_docs
        for d in selected_docs:
            self.web_worker.download_document(*d)

    def on_button_pressed(self, message: Button.Pressed) -> None:

        if message.button.id == "login_button":
            self.login()

    def on_input_submitted(self, message:Input.Submitted) -> None:
        if message.input.id == "userRnd":
            self.login()

    def login(self) -> None:
        user_id = self.query_one("#userID", Input).value
        user_pwd = self.query_one("#userPWD", Input).value
        user_rnd = self.query_one("#userRnd", Input).value

        login_v = self.query_one(LoginView)

        self.web_worker.login(user_id, user_pwd, user_rnd)

        if self.web_worker.is_login:
            login_v.remove()
            self.mount(DataTableView(self.web_worker.get_all_docs()))


if __name__ == "__main__":
    app = PaperWorkCLIApp()
    app.run()