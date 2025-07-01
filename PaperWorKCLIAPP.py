import json
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Button, Input
from textual import work

from selenium.common.exceptions import TimeoutException

from login_view import LoginView
from meun_view import MenuView, TodoMenuView
from web_worker import WebWorker
from data_table_view import DataTableView
from todo_list_view import TodoListView
from add_todo_view import AddTodoView
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

    @work(thread=True)
    def action_save_doc(self) -> None:
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
            self.action_save_doc()
        if message.button.id == "to_paper_button":
            self.to_paper()
        if message.button.id == "todo_list_button":
            self.action_show_todo_list()
        if message.button.id == "doc_list_button":
            self.action_show_doc_list()
        if message.button.id == "delete_todo_button":
            self.delete_todo()
        if message.button.id == "add_todo_button":
            self.action_add_todo()
        if message.button.id == "confirm_add_todo_button":
            self.confirm_add_todo()


    def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.input.id == "userRnd":
            self.login()

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
            self.call_from_thread(self.mount, MenuView(id="menu"),DataTableView(self.web_worker.get_all_docs(), cursor_type='row'))
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

        data_table.documents = self.web_worker.get_all_docs()
        data_table.reload_rows(unselect_all_document=True)
        msg_box.hide()

    @work(thread=True)
    def action_show_todo_list(self):
        """Switches to the to-do list view."""
        try:
            data_table = self.query_one(DataTableView)
            self.call_from_thread(data_table.remove)
            menu = self.query_one(MenuView)
            self.call_from_thread(menu.remove)
        except:
            pass
        self.call_from_thread(self.mount, TodoMenuView(id="todo_menu"))
        self.call_from_thread(self.mount, TodoListView(id="todo_list", cursor_type='row'))

    @work(thread=True)
    def action_show_doc_list(self):
        """Switches to the document list view."""
        msg_box = self.query_one(MessageBox)
        self.call_from_thread(msg_box.alert, "載入公文資料中...")
        try:
            todo_list = self.query_one(TodoListView)
            self.call_from_thread(todo_list.remove)
            todo_menu = self.query_one(TodoMenuView)
            self.call_from_thread(todo_menu.remove)
        except:
            pass
        docs = self.web_worker.get_all_docs()
        self.call_from_thread(self.mount, MenuView(id="menu"))
        self.call_from_thread(self.mount, DataTableView(docs, cursor_type='row'))
        self.call_from_thread(msg_box.hide)

    def delete_todo(self):
        """Deletes the selected to-do items."""
        todo_list = self.query_one(TodoListView)
        selected_todos = todo_list.selected_todos

        if not selected_todos:
            return

        with open("todos.json", "r+", encoding="utf-8") as f:
            todos = json.load(f)
            new_todos = [todo for todo in todos if todo["id"] not in selected_todos]
            f.seek(0)
            f.truncate()
            json.dump(new_todos, f, ensure_ascii=False, indent=4)

        todo_list.selected_todos = []
        todo_list.load_todos()

    def action_add_todo(self):
        """Shows the add to-do view."""
        self.mount(AddTodoView(id="add_todo_view"))

    def confirm_add_todo(self):
        """Confirms adding a new to-do item."""
        task = self.query_one("#task_input", Input).value
        deadline = self.query_one("#deadline_input", Input).value

        if not task or not deadline:
            return

        with open("todos.json", "r+", encoding="utf-8") as f:
            todos = json.load(f)
            new_todo = {
                "id": f"todo-{len(todos) + 1}",
                "task": task,
                "deadline": deadline,
                "status": "未開始"
            }
            todos.append(new_todo)
            f.seek(0)
            f.truncate()
            json.dump(todos, f, ensure_ascii=False, indent=4)

        self.query_one(AddTodoView).remove()
        self.query_one(TodoListView).load_todos()


if __name__ == "__main__":
    app = PaperWorkCLIApp()
    app.run()
