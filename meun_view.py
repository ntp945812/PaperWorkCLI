from textual.app import ComposeResult
from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import Input, Button, Rule, Select


class MenuView(VerticalGroup):

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Select([("承辦人", "承辦人"), ("登記桌人員", "登記桌人員")], allow_blank=False, id="role_select")
            yield Button("簽收", variant="primary", id="receipt_button", classes="hided")
            yield Button("預覽", variant="primary", id="preview_button")
            yield Button("下載", variant="primary", id="download_button")
            yield Button("轉紙本", variant="primary", id="to_paper_button")
            # yield Button("併/彙辦", variant="primary", id="combine_document_button", disabled=True)
            # yield Button("單位決行", variant="primary", id="authorize_button", disabled=True)
            # yield Button("展期", variant="primary", id="exhibition_period_button", disabled=True)
            yield Input(placeholder="搜尋", id="menu_search_input")
        yield Rule(line_style="double")
