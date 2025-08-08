from textual.app import ComposeResult
from textual.containers import VerticalGroup, HorizontalGroup
from textual.widget import Widget
from textual.widgets import Input, Button, Rule, Select


class MenuView(VerticalGroup):

    def __init__(self, role: str = "承辦人", **kwargs) -> None:
        super().__init__(**kwargs)
        self.role = role

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            if self.role == "承辦人":
                yield Select([("承辦人", "承辦人"), ("登記桌人員", "登記桌人員")], allow_blank=False, id="role_select", value="承辦人")
                yield Button("預覽", variant="primary", id="preview_button")
                yield Button("下載", variant="primary", id="download_button")
                yield Button("轉紙本", variant="primary", id="to_paper_button")
                yield Input(placeholder="搜尋", id="menu_search_input")
            # yield Button("併/彙辦", variant="primary", id="combine_document_button", disabled=True)
            # yield Button("單位決行", variant="primary", id="authorize_button", disabled=True)
            # yield Button("展期", variant="primary", id="exhibition_period_button", disabled=True)
            elif self.role == "登記桌人員":
                yield Select([("承辦人", "承辦人"), ("登記桌人員", "登記桌人員")], allow_blank=False, id="role_select", value="登記桌人員")
                yield Button("簽收", variant="primary", id="receipt_button")
                yield Button("預覽", variant="primary", id="preview_button")
                yield Input(placeholder="搜尋", id="menu_search_input")
        yield Rule(line_style="double")
