import flet as ft
from functions import config


class ChatGPTSettings:
    def __init__(self) -> None:
        self._token = config.get("GPT_TOKEN")
        self._groq_token = config.get("GROQ_TOKEN")

    async def page(self, page: ft.Page, parent: ft.Container, app):

        def on_token_change(ev):
            self._token = ev.data

        return ft.Column(
            [
                ft.TextField(
                    on_change=on_token_change, value=self._token, label="ChatGPT Token"
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Text(
                            "OR",
                            text_align=ft.TextAlign.CENTER,
                            style=ft.TextStyle(size=16),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                #                ft.Divider(),
                ft.TextField(
                    label="Groq Token",
                    value=self._groq_token,
                    on_change=lambda x: config.set("GROQ_TOKEN", x.data),
                ),
            ]
        )
