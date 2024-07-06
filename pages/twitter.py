import os
import flet as ft
from functions import config
from os import path
from twikit.twikit_async.client import Client
from functions import config, get_settings, save_settings
from flet_core.control_event import ControlEvent


class Twitter:
    def __init__(self) -> None:
        self._client = None
        self._app = None
        self._parent = None
        self._username = None
        self._password = None

    def change_username(self, value: ft.ControlEvent):
        self._username = value.data

    def change_password(self, value: ft.ControlEvent):
        self._password = value.data

    def update_page(self, page: ft.Page, content: ft.Control, args=()):
        def get_callback(ev):
            self._parent.content = content(*args)
            page.update()

        return get_callback

    def login_page(self, page: ft.Page, show_back=False):
        async def onLogin(e):
            await self.on_login_click(page)

        items = []
        if show_back:
            items.append(
                ft.FilledButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=self.update_page(page, self.after_login, args=(page,)),
                    text="Back",
                )
            )

        return ft.Column(
            [
                *items,
                ft.Row(
                    [ft.Image("assets/x.png", height=200, width=200)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.TextField(
                    label="Username",
                    on_change=self.change_username,
                ),
                ft.TextField(
                    label="Enter Password",
                    on_change=self.change_password,
                    password=True,
                    can_reveal_password=True,
                ),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.FilledButton(
                            text="Login to X",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_GREY_500, color=ft.colors.WHITE
                            ),
                            on_click=onLogin,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

    async def on_login_click(self, page: ft.Page):
        if not (self._username and self._password):
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("Please enter username and password"),
            )
            page.show_dialog(dialog)
            return

        if not self._client:
            self._client = Client()

        try:
            await self._client.login(
                auth_info_1=self._username, password=self._password
            )
        except Exception as er:
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(str(er)),
            )
            page.show_dialog(dialog)
            return

        if not os.path.exists("sessions/twitter"):
            os.makedirs("sessions/twitter", exist_ok=True)

        userId = await self._client.user_id()
        me = await self._client.get_user_by_id(userId)
        data = {
            "userId": userId,
            "name": me.name,
            "image": me.profile_image_url,
            "username": self._username,
            "password": self._password,
        }
        settings = get_settings()
        accounts = settings.get("twitter_accounts", {})
        path = f"sessions/twitter/{self._username}.json"
        self._client.save_cookies(path)
        data["path"] = path
        if not settings.get("twitter_accounts"):
            settings["twitter_accounts"] = {}
        settings["twitter_accounts"][me.screen_name] = data
        save_settings(settings)

        page.update()

    def accounts(self):
        return get_settings().get("twitter_accounts", {})

    async def page(self, page: ft.Page, parent: ft.Container, app):
        self._app = app
        self._parent = parent

        accounts = self.accounts()
        if not accounts:
            return self.login_page(page)
        return self.after_login(page)

    def after_login(self, page: ft.Page):

        async def addAccount(ev):
            self._parent.content = self.login_page(page, show_back=True)
            page.update()

        accounts = self.accounts()
        rows = [
            ft.DataRow(
                [
                    ft.DataCell(ft.Checkbox()),
                    ft.DataCell(
                        ft.Image(data["image"], border_radius=100, height=30, width=30)
                    ),
                    ft.DataCell(ft.Text(data["name"])),
                    ft.DataCell(ft.Text(data["username"])),
                ]
            )
            for username, data in accounts.items()
        ]
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.FilledButton(
                            text="Add Account",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_GREY_500, color=ft.colors.WHITE
                            ),
                            on_click=addAccount,
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.RED, color=ft.colors.WHITE
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.DataTable(
                    column_spacing=100,
                    columns=[
                        ft.DataColumn(label=ft.Text("")),
                        ft.DataColumn(label=ft.Text("Profile")),
                        ft.DataColumn(label=ft.Text("Name")),
                        ft.DataColumn(label=ft.Text("Username")),
                    ],
                    rows=rows,
                ),
            ]
        )
