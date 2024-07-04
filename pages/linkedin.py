import os, json
import flet as ft
from functions import config
from os import path
from linkedin_api import Linkedin as Client
from flet_core.control_event import ControlEvent
from requests.cookies import RequestsCookieJar


class LinkedIN:
    def __init__(self) -> None:
        self._username = config.get("LINKEDIN_USERNAME")
        self._password = config.get("LINKEDIN_PASSWORD")
        self._settings_path = config.get("LINKEDIN_SETTINGS_PATH")
        self._client = None

    def process_login(self):
        pass

    def change_username(self, value: ft.ControlEvent):
        self._username = value.data

    def change_password(self, value: ft.ControlEvent):
        self._password = value.data

    def login_page(self, page: ft.Page):
        return ft.Column(
            [
                ft.Row(
                    [ft.Image("assets/linkedin.png", height=200, width=200)],
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
                            text="Login to LinkedIn",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_GREY_500, color=ft.colors.WHITE
                            ),
                            on_click=lambda x: self.on_login_click(page),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

    def on_login_click(self, page: ft.Page):
        if not (self._username and self._password):
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("Please enter username and password"),
            )
            page.show_dialog(dialog)
            return

        try:
            self.client()
        except Exception as er:
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(str(er)),
            )
            page.show_dialog(dialog)
            return

        if not path.exists("sessions"):
            os.mkdir("sessions")

        settings_path = os.path.join("sessions", f"{self._username}.json")
        cookies = {x: y for x, y in self._client.client.session.cookies.items()}
        with open(settings_path, "w") as f:
            json.dump(cookies, f)

        config.set("LINKEDIN_USERNAME", self._username)
        config.set("LINKEDIN_PASSWORD", self._password)
        config.set("LINKEDIN_SETTINGS_PATH", settings_path)
        self._settings_path = settings_path

        page.update()

    async def page(self, page: ft.Page, parent: ft.Container, app):
        if not self._settings_path:
            return self.login_page(page)
        return await self.after_login()

    def client(self):
        if not self._client:
            cookies = RequestsCookieJar()

            with open(self._settings_path, "r") as f:
                data = json.load(f)
                for key, value in data.items():
                    cookies.set(key, value)

            self._client = Client(self._username, self._password, cookies=cookies)
        return self._client

    async def after_login(self):
        me = self.client().get_user_profile()
        prof = me["miniProfile"]
        name = prof["firstName"] + f" {prof['lastName']}"

        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "Logged in as",
                            style=ft.TextStyle(size=25),
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=20),
                        ft.Image(
                            "assets/linkedin.png",
                            height=200,
                            width=200
                        ),
                        ft.Text(name,
                                text_align=ft.TextAlign.CENTER
                                ),
                    ]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
