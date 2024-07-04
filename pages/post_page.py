import flet as ft
from flet_core.control_event import ControlEvent


class PostPage:
    def __init__(self) -> None:
        self._page = None
        self._parent = None
        self._app = None

        self._text = ""
        self._files = []

    def on_text_change(self, value: ft.ControlEvent):
        self._text = value.data

    async def file_picker_result(self, result: ft.FilePickerResultEvent):
        self._files.extend(result.files)
        if self._page:
            self._parent.content = await self.page(self._page, self._parent, self._app)
            self._page.update()

    def show_file_picker(self, page: ft.Page):
        picker = ft.FilePicker(on_result=self.file_picker_result)
        page.overlay.append(picker)
        page.update()
        picker.pick_files()
    
    async def click_send(self, ev: ControlEvent):
        if not (self._text or self._files):
            return

        from app import App
        app: App = self._app
        await app.send_message(
            self._text,
            files=self._files or None
        )

    async def page(self, page: ft.Page, parent: ft.Container, app):
        self._page = page
        self._parent = parent
        self._app = app

        items = []
        if self._files:
            items.append(
                ft.Row(
                    [
                        ft.Image(src=img.path, height=80, width=80, border_radius=10)
                        for img in self._files
                    ]
                )
            )

        items.extend(
            [
                ft.TextField(
                    label="Enter text..",
                    label_style=ft.TextStyle(),
                    hint_text="Enter your post text here..",
                    min_lines=10,
                    on_change=self.on_text_change,
                    multiline=True,
                    value=self._text
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ATTACH_FILE_ROUNDED,
                            on_click=lambda x: self.show_file_picker(page),
                        ),
                        ft.FilledButton(text="Send now", icon="send",
                                        on_click=self.click_send),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ]
        )

        return ft.Column(items)
