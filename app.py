import flet as ft
from typing import List
from logging import getLogger

from pages.telegram import Telegram
from pages.instagram import Instagram
from pages.post_page import PostPage
from pages.linkedin import LinkedIN
from pages.chat_gpt import ChatGPTSettings
from pages.twitter import Twitter


class App:
    def __init__(self, initial_page: str = "create_post") -> None:
        self.page = initial_page
        self.current_page_obj = None
        self.parent = None
        self._drawer = None
        self._logger = getLogger("app")

        self._telegram = Telegram()
        self._instagram = Instagram()
        self._create = PostPage()
        self._linkedin = LinkedIN()
        self._chatgpt = ChatGPTSettings()
        self._twitter = Twitter()

    def routes(self):
        data = {
            "create_post": {
                "title": "Create Post",
                "callback": self._create.page,
                "image": "assets/quill.png",
            },
            "instagram": {
                "title": "Instagram",
                "callback": self._instagram.page,
                "image": "assets/instagram.png",
            },
            "twitter": {
                "title": "X | Twitter",
                "callback": self._twitter.page,
                "image": "assets/x.png",
            },
            "linkedin": {
                "title": "LinkedIn",
                "callback": self._linkedin.page,
                "image": "assets/linkedin.png",
            },
            "telegram": {
                "title": "Telegram",
                "callback": self._telegram.telegram_page,
                "image": "assets/telegram.png",
            },
            "chatgpt": {
                "title": "ChatGPT",
                "callback": self._chatgpt.page,
                "image": "assets/settings.png",
            },
        }
        for x in data:

            def on_click(x):
                async def move(_):
                    await self.navigate(x)

                return move

            data[x]["on_click"] = on_click(x)

        return data

    async def navigate(self, page_id):
        self.page = page_id
        print("Navigating page")

        if self.parent:
            callback = self.routes()[self.page]["callback"]

            self.parent.content = await callback(
                self.current_page_obj, self.parent, self
            )
            self._drawer.content = self.drawer_content()

            self.current_page_obj.update()
        else:
            self.render_page(self.current_page_obj)

    def get_sidebar_content(self):
        items = []
        for page_id, data in self.routes().items():
            if page_id in ["chatgpt", "instagram"]:
                items.append(ft.Divider())
            items.append(
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(data["title"], style=ft.TextStyle(size=20)),
                        style=ft.ListTileStyle.DRAWER,
                        on_click=data["on_click"],
                        leading=ft.Image(data["image"], width=30, height=30),
                    ),
                    border_radius=10,
                    bgcolor=(
                        ft.colors.WHITE10
                        if page_id == self.page
                        else ft.colors.TRANSPARENT
                    ),
                )
            )
        return items

    async def send_message(self, text: str, files: List[str] = None):
        for provider in [
            self._telegram,
            #            self._instagram,
            self._linkedin,
            self._twitter,
        ]:
            if hasattr(provider, "send_message"):
                try:
                    await provider.send_message(text, files)
                except Exception as er:
                    self._logger.exception(er)

    def drawer_content(self):
        return ft.Column(
            [
                ft.Column(self.get_sidebar_content()),
            ],
            #            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    async def render_page(self, page: ft.Page):
        self.current_page_obj = page
        page.clean()
        callback = self.routes()[self.page]["callback"]
        #        print(callback, self.page)

        self._drawer = ft.Container(
            content=self.drawer_content(),
            width=page.width // 4,
            bgcolor=ft.colors.BLACK38,
            padding=10,
            height=page.window_height,
        )

        item_container = ft.Container(
            #                          bgcolor=ft.colors.WHITE,
            height=page.window_height,
            #                        width=page,
            padding=10,
            scale=ft.Scale.scale_x,
            expand=1,
            #                        padding=10
        )
        item_container.content = await callback(page, item_container, self)
        self.parent = item_container
        page.add(
            ft.Row(
                [
                    ft.Column(
                        [self._drawer],
                        #       expand=True,
                        # expand_loose=True
                    ),
                    item_container,
                ],
                expand=True,
                expand_loose=True,
            )
        )


if __name__ == "__main__":
    app = App()
    ft.app(app.render_page)
