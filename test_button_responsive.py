"""
Simple Button Test - Verify Flet UI is responsive
Run with: flet run test_button_responsive.py
"""

import flet as ft

def main(page: ft.Page):
    page.title = "Button Responsiveness Test"
    page.padding = 20

    click_count = ft.Ref[ft.Text]()
    dialog_test = ft.Ref[ft.AlertDialog]()
    snackbar_test = ft.Ref[ft.SnackBar]()

    def on_button_click(e):
        current = int(click_count.current.value)
        click_count.current.value = str(current + 1)
        page.update()

    def show_dialog(e):
        dlg = ft.AlertDialog(
            title=ft.Text("Test Dialog"),
            content=ft.Text("If you see this, dialogs are working!"),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog())
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dialog():
        if page.dialog:
            page.dialog.open = False
            page.update()

    def show_snackbar(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Snackbar is working!"),
            action="OK"
        )
        page.snack_bar.open = True
        page.update()

    def test_form_dialog(e):
        name_field = ft.TextField(label="Name", autofocus=True)
        email_field = ft.TextField(label="Email")

        def save_form(e):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Saved: {name_field.value} - {email_field.value}")
            )
            page.snack_bar.open = True
            close_dialog()
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Form Dialog Test"),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    email_field
                ], tight=True),
                width=400
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.ElevatedButton("Save", on_click=save_form)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    page.add(
        ft.Column([
            ft.Text("Flet UI Responsiveness Test", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),

            ft.Text("Test 1: Simple Button Click"),
            ft.Row([
                ft.ElevatedButton("Click Me", on_click=on_button_click),
                ft.Text("Clicks: "),
                ft.Text("0", ref=click_count)
            ]),

            ft.Divider(),
            ft.Text("Test 2: Dialog System"),
            ft.ElevatedButton("Show Dialog", on_click=show_dialog),

            ft.Divider(),
            ft.Text("Test 3: SnackBar"),
            ft.ElevatedButton("Show SnackBar", on_click=show_snackbar),

            ft.Divider(),
            ft.Text("Test 4: Form Dialog (like user/listing forms)"),
            ft.ElevatedButton("Show Form Dialog", on_click=test_form_dialog),

            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Text("Results:", weight=ft.FontWeight.BOLD),
                    ft.Text("✓ If buttons respond = Event handlers work", size=12),
                    ft.Text("✓ If dialogs open = Dialog system works", size=12),
                    ft.Text("✓ If forms save = CRUD UI pattern works", size=12),
                    ft.Text("", size=4),
                    ft.Text("If any test fails, the issue is in Flet UI layer",
                           color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                ]),
                padding=20,
                bgcolor=ft.Colors.BLUE_GREY_50,
                border_radius=10
            )
        ], spacing=15)
    )

if __name__ == "__main__":
    ft.app(target=main)
