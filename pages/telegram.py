import os, asyncio
import flet as ft
from flet import Image
from asyncio import get_event_loop, new_event_loop
from functions import config, get_settings, save_settings
from telethon.utils import get_display_name
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, SessionExpiredError
from flet_core.control_event import ControlEvent
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class Telegram:
    def __init__(self) -> None:
        self._tg_client = None
        self._phone_number = None
        self._parent = None
        self._code = None
        self._loop = None
        self._entered_code = None
        self._password = None
        self._path = config.get("SESSION_PATH")
        self._cached_dialogs = None
        self._me = None
        self._data = {}

    def on_phone_change(self, value: ControlEvent):
        self._phone_number = value.data

    async def get_tg_profile(self, username):
        async with ClientSession() as ses:
            data = await ses.get("https://t.me/" + username)
            data = await data.read()
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        itag = soup.find("img", "tgme_page_photo_image")
        if itag:
            return itag.get("src")

    def telegram_login_page(self, page: ft.Page):

        async def send_code(x):
            await self.send_login_code(page)

        return ft.Column(
            [
                ft.Row(
                    [ft.Image(src="assets/telegram.png", width=200, height=200)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.TextField(
                    label="Enter Phone Number",
                    on_change=self.on_phone_change,
                    keyboard_type=ft.KeyboardType.PHONE,
                ),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.FilledButton(
                            text="Login to Telegram",
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.BLUE_400,
                            ),
                            on_click=send_code,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

    def text_change(self, id):
        def listen(value: ControlEvent):
            self._data[id] = value.data

        return listen

    async def add_channel(self, ev):
        channelUsername = self._data.get("add_channel", "").lower()

        if not channelUsername:
            return
        settings = get_settings()
        tg_channel = await self._tg_client.get_entity(channelUsername)
        if not settings.get("telegram_channels"):
            settings["telegram_channels"] = {}
        settings["telegram_channels"][channelUsername] = {
            "name": get_display_name(tg_channel),
            "image": (await self.get_tg_profile(channelUsername)) or "assets/telegram.png",
        }
        save_settings(settings)

    async def telegram_home_page(self, page: ft.Page):
        if not self._me:
            if not self._tg_client:
                self._tg_client = TelegramClient(
                    self._path,
                    api_id=config.get("TG_API_ID"),
                    api_hash=config.get("TG_API_HASH"),
                )
                await self._tg_client.connect()
            self._me = await self._tg_client.get_me()

        items = [
            ft.ListTile(
                title=ft.Text(get_display_name(self._me)),
                bgcolor=ft.colors.BLACK38,
                trailing=ft.ElevatedButton(text="Logout"),
            ),
            ft.Row(
                [
                    ft.TextField(on_change=self.text_change("add_channel")),
                    ft.Container(width=20),
                    ft.FilledButton(text="Add Channel", on_click=self.add_channel),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
        ]
        channels = get_settings().get("telegram_channels", {})

        items.append(
            ft.Text(
                "Telegram Channels:",
                style=ft.TextStyle(
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    #                    color=ft.colors.BLACK,
                ),
            )
        )

        if channels:
            tiles = []
            for channel, data in channels.items():
                tiles.append(
                    ft.DataRow(
                        [
                            ft.DataCell(
                                ft.Image(
                                    data.get("image") or "assets/telegram.png",
                                    width=30,
                                    height=30,
                                    border_radius=100,
                                ),
                            ),
                            ft.DataCell(
                                ft.Text(data.get("name", "")),
                            ),
                        ]
                    )
                )
            items.append(
                ft.DataTable(
                    columns=[
                        ft.DataColumn(
                            label=ft.Text("Image"),
                        ),
                        ft.DataColumn(ft.Text("Name")),
                    ],
                    rows=tiles,
                    expand=True,
                    width=700,
                    column_spacing=10,
                )
            )
        else:
            items.append(
                ft.Text(
                    "You have not added any channels yet. Click the button above to add a channel",
                    opacity=0.6,
                )
            )
        return ft.Column(items)

    async def telegram_page(self, page: ft.Page, parent: ft.Container, app):
        self._parent = parent

        if config.get("SESSION_PATH"):
            return await self.telegram_home_page(page)

        return self.telegram_login_page(page)

    def on_code_change(self, value: ControlEvent):
        self._entered_code = value.data

    def on_password_change(self, value: ControlEvent):
        self._password = value.data

    def telegram_password(self, page: ft.Page):

        async def onClick(x):
            try:
                await self._tg_client.sign_in(password=self._password)
            except Exception as er:
                dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text(str(er)),
                )
                page.show_dialog(dialog)
                return

            await self.complete_signup()

        return ft.Column(
            [
                ft.Row(
                    [ft.Image(src="assets/telegram.png", width=200, height=200)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.TextField(
                    label="Enter Password",
                    on_change=self.on,
                    password=True,
                    can_reveal_password=True,
                ),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.FilledButton(
                            text="Continue",
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.BLUE_400,
                            ),
                            on_click=onClick,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

    async def complete_signup(self):
        config.set("SESSION_PATH", self._path)

    def telegram_otp_page(self, page: ft.Page):

        async def try_sign_in(x):
            try:
                await self._tg_client.sign_in(
                    phone=self._phone_number,
                    code=self._entered_code,
                    phone_code_hash=self._code.phone_code_hash,
                )
            except SessionExpiredError:
                self._parent.content = self.telegram_password(page)
                page.update()
                return
            await self.complete_signup()

        return ft.Column(
            [
                ft.Row(
                    [ft.Image(src="assets/telegram.png", width=200, height=200)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.TextField(
                    label="Enter Login code",
                    on_change=self.on_code_change,
                    keyboard_type=ft.KeyboardType.NUMBER,
                ),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.FilledButton(
                            text="Continue",
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=ft.colors.BLUE_400,
                            ),
                            on_click=try_sign_in,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )

    async def send_message(self, text, files=None):
        await self._get_client()
        channels = get_settings().get("telegram_channels", {})
        usernames = channels.keys()
        for chat in usernames:
            try:
                await self._tg_client.send_message(
                    chat,
                    message=text,
                    file=files
                )
            except Exception as er:
                print(er)


    async def _get_client(self):
        if not self._tg_client:
            self._tg_client = TelegramClient(
                self._path,
                api_id=config.get("TG_API_ID"),
                api_hash=config.get("TG_API_HASH"),
            )
            await self._tg_client.connect()
        return self._tg_client

    async def send_login_code(self, page: ft.Page):
        if not self._phone_number:
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("Please enter your phone number to login to Telegram"),
            )
            page.show_dialog(dialog)
            return

        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        path = os.path.join("sessions", self._phone_number)
        self._path = path

        try:
            await self._get_client()
            self._code = await self._tg_client.send_code_request(
                phone=self._phone_number
            )
            print(self._code)

            if self._parent:
                self._parent.content = self.telegram_otp_page(page)
                page.update()

        except Exception as er:
            print(er)
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(str(er)),
            )
            page.show_dialog(dialog)


#            page.update()
