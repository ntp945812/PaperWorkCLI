from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Input, Button, Label
from rich.text import Text


class LoginView(VerticalGroup):

    def compose(self) -> ComposeResult:

        yield Label(Text("二代公文整合系統-自然人憑證登入",style="bold deep_sky_blue3",justify="right"))
        yield Input(placeholder="PinCode", password=True, id="pinCode")
        yield Input(placeholder="驗證碼",id="userRnd")
        yield Button("登入", variant="primary")
