import flet as ft
import time


def settimeoutmessage(page: ft.Page, textarea: ft.Column, text: str, color=ft.Colors.BLUE, timeout: int = 3) -> None:
    textarea.controls.clear()
    textarea.controls.append(ft.Text(text, color=color))
    textarea.update()

    def clear_message():
        time.sleep(timeout)
        textarea.controls.clear()
        textarea.update()

    page.run_thread(clear_message)


def setloading(page: ft.Page, textarea: ft.Column, text: str = "Učitavanje...", color=ft.Colors.BLUE) -> None:
    textarea.controls.clear()
    row = ft.Row(
        [
            ft.Text(text, color=color),
            ft.VerticalDivider(width=1, color="grey"),  # separator
            ft.ProgressRing(width=16, height=16, color=color),
        ],
        alignment="start",
        spacing=5,
    )
    textarea.controls.append(row)
    textarea.update()
