from textual.app import ComposeResult
from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import Input, Button, Rule


class MenuView(VerticalGroup):

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(Button("下載", variant="primary", id="download_button")
                              , Button("轉紙本", variant="primary", id="to_paper_button")
                              , Button("併/彙辦", variant="primary", id="combine_document_button")
                              , Button("單位決行", variant="primary", id="authorize_button")
                              , Button("展期", variant="primary", id="exhibition_period_button")
                              , Input(placeholder="搜尋", id="menu_search_input"))
        yield Rule(line_style="double")