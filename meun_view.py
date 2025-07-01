from textual.app import ComposeResult
from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import Input, Button, Rule


class MenuView(VerticalGroup):

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Button("下載", variant="primary", id="download_button")
            yield Button("轉紙本", variant="primary", id="to_paper_button")
            yield Button("併/彙辦", variant="primary", id="combine_document_button", disabled=True)
            yield Button("單位決行", variant="primary", id="authorize_button", disabled=True)
            yield Button("展期", variant="primary", id="exhibition_period_button", disabled=True)
            yield Button("公文列表", variant="primary", id="doc_list_button")
            yield Button("代辦事項", variant="primary", id="todo_list_button")
            yield Input(placeholder="搜尋", id="menu_search_input")
        yield Rule(line_style="double")

class TodoMenuView(VerticalGroup):
    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Button("新增", variant="primary", id="add_todo_button")
            yield Button("刪除", variant="primary", id="delete_todo_button")
        yield Rule(line_style="double")