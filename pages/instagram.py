import os
import flet as ft
from functions import config
from os import path
from instagrapi import Client

from flet_core.control_event import ControlEvent


class Instagram:
    def __init__(self) -> None:
        self._username = config.get("IG_USERNAME")
        self._password = config.get("IG_PASSWORD")
        self._settings_path = config.get("IG_SETTINGS_PATH")
        self._client = None
        self._me = None

    def change_username(self, value: ft.ControlEvent):
        self._username = value.data

    def change_password(self, value: ft.ControlEvent):
        self._password = value.data

    def login_page(self, page: ft.Page):
        return ft.Column(
            [
                ft.Row(
                    [ft.Image("assets/instagram.png", height=200, width=200)],
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
                            text="Login to Instagram",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.RED, color=ft.colors.WHITE
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

        if not self._client:
            self._client = Client()

        try:
            self._client.login(self._username, self._password)
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
        self._client.dump_settings(settings_path)
        config.set("IG_USERNAME", self._username)
        config.set("IG_PASSWORD", self._password)
        config.set("IG_SETTINGS_PATH", settings_path)
        page.update()

    async def page(self, page: ft.Page, parent: ft.Container, app):
        if not self._settings_path:
            return self.login_page(page)
        return self.after_login()

    def after_login(self):
        if not self._me:
            if not self._client:
                self._client = Client()
                self._client.load_settings(self._settings_path)
            self._me = self._client.account_info()
        items = [
            ft.Text(
                "Logged in as",
                style=ft.TextStyle(
                    size=25,
                ),
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                [
                    ft.Image(
                        self._me.profile_pic_url,
                        #                        width=300,
                        #                       height=300,
                        border_radius=100,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [ft.Text(self._me.full_name, style=ft.TextStyle(size=18))],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row([ft.Text(self._me.username)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                [
                    ft.ElevatedButton(
                        text="Logout",
                        bgcolor=ft.colors.RED_400,
                        color=ft.colors.WHITE,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ]

        return ft.Column(items)
