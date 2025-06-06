from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widgets import Input, Button, Label

from textual_imageview.viewer import ImageViewer
from PIL import Image

from rich.text import Text

from web_worker import WebWorker

from pathlib import Path
import tempfile

TEMP_DIR = tempfile.gettempdir()

CAPTCHA_IMG_PATH = Path(TEMP_DIR).joinpath('captcha_login.png')

class LoginView(VerticalGroup):

    def __init__(self, web_worker: WebWorker):
        super().__init__()
        self.web_worker = web_worker
        self.web_worker.download_user_rnd_img()

    def compose(self) -> ComposeResult:
        yield Label(Text("二代公文整合系統-帳號密碼登入", style="bold deep_sky_blue3", justify="right"))
        yield Input(placeholder="帳號", id="userID")
        yield Input(placeholder="密碼", password=True, id="userPWD")
        yield ImageViewer(Image.open(CAPTCHA_IMG_PATH))
        yield Input(placeholder="驗證碼", id="userRnd")
        yield Button("登入", variant="primary", id="login_button")
