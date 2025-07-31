from selenium.common.exceptions import TimeoutException
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Input, Select

from data_table_view import DataTableView
from login_view import LoginView
from message_box import MessageBox
from meun_view import MenuView
from web_worker import WebWorker


class PaperWorkCLIApp(App):
    """A Textual app to manage stopwatches."""

    def __init__(self):
        super().__init__()
        self.web_worker = WebWorker()

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "refresh_doc", "Refresh")
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

    def action_refresh_doc(self):
        match self.web_worker.current_role:
            case "承辦人":
                self.refresh_officer_doc()
            case "登記桌人員":
                self.refresh_checkin_table_doc()

    @work(thread=True)
    def save_doc(self) -> None:
        """Save selected document to unzip and merge"""
        msg_box = self.query_one(MessageBox)
        msg_box.alert("本文、附件下載中...")
        data_table = self.query_one(DataTableView)
        selected_docs = data_table.selected_docs
        for d in selected_docs:
            self.web_worker.download_document(*d)

        self.call_from_thread(data_table.unselect_all_document)
        msg_box.hide()

    def on_button_pressed(self, message: Button.Pressed) -> None:

        if message.button.id == "login_button":
            self.login()
        if message.button.id == "download_button":
            self.save_doc()
        if message.button.id == "to_paper_button":
            self.to_paper()
        if message.button.id == "receipt_button":
            self.receipt_document_from_table()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.input.id == "userRnd":
            self.login()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "role_select":
            current_role = self.web_worker.current_role
            match current_role, event.value:
                case "登記桌人員", "承辦人":
                    self.switch_to_officer()
                case "承辦人", "登記桌人員":
                    self.switch_to_checkin_table()

    @work(thread=True)
    def login(self) -> None:

        msg_box = self.query_one(MessageBox)
        msg_box.alert("登入中...")

        user_id = self.query_one("#userID", Input).value
        user_pwd = self.query_one("#userPWD", Input).value
        user_rnd = self.query_one("#userRnd", Input).value

        login_v = self.query_one(LoginView)

        try:
            self.web_worker.login(user_id, user_pwd, user_rnd)
        except TimeoutException as timeout:
            self.call_from_thread(msg_box.alert, timeout.msg, hide_after=2.5)

        if self.web_worker.is_login:
            msg_box.hide()
            login_v.remove()
            msg_box.alert("載入公文資料中...")
            self.call_from_thread(self.mount, MenuView(id="menu", classes="officer"),
                                  DataTableView(self.web_worker.get_officer_all_docs(), cursor_type='row'))
            msg_box.hide()
        else:
            login_v.remove()
            self.call_from_thread(self.mount, LoginView(web_worker=self.web_worker))

    @work(thread=True)
    def to_paper(self) -> None:
        msg_box = self.query_one(MessageBox)
        msg_box.alert("轉紙本作業中...")
        data_table = self.query_one(DataTableView)
        for selected_doc in data_table.selected_docs:
            self.web_worker.transfer_document_to_paper(*selected_doc)

        data_table.documents = self.web_worker.get_officer_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        msg_box.hide()

    @work(thread=True)
    def switch_to_checkin_table(self) -> None:
        msg_box = self.query_one(MessageBox)
        msg_box.alert("切換至登記桌...")
        self.web_worker.switch_to_checkin_table()
        data_table = self.query_one(DataTableView)
        data_table.documents = self.web_worker.get_table_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        menu_buttons = self.query("MenuView Button")
        for btn in menu_buttons:
            if btn.id == "receipt_button":
                btn.remove_class("hided")
            else:
                btn.add_class("hided")
        msg_box.hide()

    @work(thread=True)
    def switch_to_officer(self) -> None:
        msg_box = self.query_one(MessageBox)
        msg_box.alert("切換至承辦人...")
        self.web_worker.switch_to_officer()
        data_table = self.query_one(DataTableView)
        data_table.documents = self.web_worker.get_officer_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        menu_buttons = self.query("MenuView Button")
        for btn in menu_buttons:
            if btn.id == "receipt_button":
                btn.add_class("hided")
            else:
                btn.remove_class("hided")
        msg_box.hide()

    @work(thread=True)
    def refresh_officer_doc(self):
        msg_box = self.query_one(MessageBox)
        msg_box.alert("重新整理...")
        data_table = self.query_one(DataTableView)
        data_table.documents = self.web_worker.get_officer_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        msg_box.hide()

    @work(thread=True)
    def refresh_checkin_table_doc(self):
        msg_box = self.query_one(MessageBox)
        msg_box.alert("重新整理...")
        data_table = self.query_one(DataTableView)
        data_table.documents = self.web_worker.get_table_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        msg_box.hide()

    @work(thread=True)
    def receipt_document_from_table(self):
        if self.web_worker.current_role != "登記桌人員":
            return

        msg_box = self.query_one(MessageBox)
        msg_box.alert("簽收中...")

        data_table = self.query_one(DataTableView)
        doc_ids = [d[1] for d in data_table.selected_docs]
        self.web_worker.receipt_document_from_table(doc_ids)
        self.web_worker.distribute_document(doc_ids)

        data_table.documents = self.web_worker.get_table_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        msg_box.hide()


if __name__ == "__main__":
    app = PaperWorkCLIApp()
    app.run()
