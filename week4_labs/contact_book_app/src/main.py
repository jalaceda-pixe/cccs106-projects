import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    # --- Page & Theme ---
    page.title = "Contact Book"
    page.theme_mode = ft.ThemeMode.DARK   # Start in dark mode
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 520
    page.window_height = 720
    page.padding = 20

    # --- DB init ---
    db_conn = init_db()

    # --- Top bar: Title, Search, Theme Toggle ---
    title = ft.Text("Contact Book", size=22, weight=ft.FontWeight.BOLD)
    search_field = ft.TextField(
        hint_text="Search by name, phone, or email...",
        width=320,
        autofocus=False,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_field.value),
        prefix=ft.Icon(ft.Icons.SEARCH),  # ✅ Fixed capitalization
    )

    theme_switch = ft.Switch(
        value=True,
        label="Dark",
        on_change=lambda e: toggle_theme(page, e.control.value)
    )

    # Use Container(expand=1) instead of ft.Spacer() for older Flet versions
    top_row = ft.Row(
        controls=[
            title,
            ft.Container(expand=1),   # Works like a spacer
            search_field,
            theme_switch,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # --- Input fields & Add Button ---
    name_input = ft.TextField(label="Name", width=360)
    phone_input = ft.TextField(label="Phone", width=360)
    email_input = ft.TextField(label="Email", width=360)

    inputs = (name_input, phone_input, email_input)

    add_button = ft.FilledButton(
        "Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    form_card = ft.Card(
        content=ft.Container(
            ft.Column([
                ft.Text("Add a new contact", weight=ft.FontWeight.BOLD),
                name_input,
                ft.Row([phone_input, email_input],
                       alignment=ft.MainAxisAlignment.START, spacing=12),
                ft.Row([ft.Container(expand=1), add_button],
                       alignment=ft.MainAxisAlignment.END),
            ]),
            padding=16,
        ),
        elevation=6,
        margin=ft.margin.only(bottom=12),
    )

    # --- Contacts list ---
    contacts_list_view = ft.ListView(expand=1, spacing=8, padding=ft.padding.only(top=8))

    # Layout assembly
    page.add(
        ft.Column(
            controls=[
                top_row,
                form_card,
                ft.Text("Contacts", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                contacts_list_view,
            ],
            tight=False,
            spacing=12,
        )
    )

    # Initial load
    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def toggle_theme(page: ft.Page, is_dark: bool):
    """Toggles dark/light mode dynamically."""
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT

    def update_label(controls):
        for c in controls:
            if isinstance(c, ft.Switch):
                c.label = "Dark" if c.value else "Light"
            # Recursively update inside containers
            if isinstance(c, (ft.Row, ft.Column, ft.Container, ft.Card, ft.ListView)):
                if hasattr(c, "controls"):
                    update_label(c.controls)

    update_label(page.controls)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
