import flet as ft
from functions import config

class ChatGPTSettings:
    def __init__(self) -> None:
        self._token = config.get("GPT_TOKEN")

    async def page(self, page: ft.Page, parent: ft.Container, app):

        def on_token_change(ev):
            self._token = ev.data

        return ft.Column(
            [
                ft.TextField(
                    on_change=on_token_change,
                    value=self._token,
                    label="ChatGPT Token"
                )
            ]
        )
    