import flet as ft
import re
from database import add_contact_db, get_all_contacts_db, update_contact_db, delete_contact_db


# ---------------------- CONTACT CARD ---------------------- #
def _create_contact_card(page: ft.Page, contact, db_conn, refresh_callback):
    """Return a card representing one contact."""
    contact_id, name, phone, email = contact

    def handle_edit(e):
        open_edit_dialog(page, contact, db_conn, refresh_callback)

    def handle_delete(e):
        open_delete_confirmation(page, contact_id, db_conn, refresh_callback)

    left = ft.Column([
        ft.Text(name, weight=ft.FontWeight.BOLD, size=14),
        ft.Row([
            ft.Icon(ft.Icons.PHONE, size=14),
            ft.Text(phone or "-", size=12),
            ft.Container(width=10),
            ft.Icon(ft.Icons.EMAIL, size=14),
            ft.Text(email or "-", size=12),
        ], spacing=8)
    ], expand=1)

    actions = ft.Row([
        ft.IconButton(icon=ft.Icons.EDIT, tooltip="Edit", on_click=handle_edit),
        ft.IconButton(icon=ft.Icons.DELETE, tooltip="Delete", on_click=handle_delete),
    ])

    return ft.Card(
        content=ft.Container(
            ft.Row([left, actions], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
        ),
        elevation=3,
        margin=ft.margin.symmetric(vertical=6),
    )


# ---------------------- DISPLAY CONTACTS ---------------------- #
def display_contacts(page: ft.Page, contacts_list_view: ft.ListView, db_conn, search: str | None = None):
    """Display all contacts."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search)

    if not contacts:
        contacts_list_view.controls.append(ft.Text("No contacts found.", italic=True))
    else:
        for contact in contacts:
            card = _create_contact_card(page, contact, db_conn, lambda: display_contacts(page, contacts_list_view, db_conn, search))
            contacts_list_view.controls.append(card)

    page.update()


# ---------------------- ADD CONTACT ---------------------- #
def add_contact(page: ft.Page, inputs, contacts_list_view: ft.ListView, db_conn):
    """Add a new contact with validation."""
    name_input, phone_input, email_input = inputs
    name = (name_input.value or "").strip()
    phone = (phone_input.value or "").strip()
    email = (email_input.value or "").strip()

    # Reset previous error texts
    name_input.error_text = None
    phone_input.error_text = None
    email_input.error_text = None

    # --- VALIDATION ---
    is_valid = True

    # 1️⃣ Name validation
    if not name:
        name_input.error_text = "Name cannot be empty"
        is_valid = False

    # 2️⃣ Phone validation (numbers only, 11 digits)
    if not re.fullmatch(r"^\d{11}$", phone):
        phone_input.error_text = "Phone must be 11 digits (numbers only)"
        is_valid = False

    # 3️⃣ Email validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        email_input.error_text = "Please enter a valid email address"
        is_valid = False

    if not is_valid:
        page.update()
        return  # Stop if invalid input

    # --- Add contact to DB ---
    add_contact_db(db_conn, name, phone, email)

    # Clear inputs
    for field in inputs:
        field.value = ""
        field.error_text = None

    display_contacts(page, contacts_list_view, db_conn)
    _show_snackbar(page, f"Contact '{name}' added successfully!")


# ---------------------- EDIT DIALOG ---------------------- #
def open_edit_dialog(page: ft.Page, contact, db_conn, refresh_callback):
    """Show edit dialog."""
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(label="Name", value=name, width=320)
    edit_phone = ft.TextField(label="Phone", value=phone, width=320)
    edit_email = ft.TextField(label="Email", value=email, width=320)

    def on_save(e):
        # Reset errors
        edit_name.error_text = None
        edit_phone.error_text = None
        edit_email.error_text = None

        new_name = (edit_name.value or "").strip()
        new_phone = (edit_phone.value or "").strip()
        new_email = (edit_email.value or "").strip()

        is_valid = True

        # 1️⃣ Name check
        if not new_name:
            edit_name.error_text = "Name cannot be empty"
            is_valid = False

        # 2️⃣ Phone check
        if not re.fullmatch(r"^\d{11}$", new_phone):
            edit_phone.error_text = "Phone must be 11 digits (numbers only)"
            is_valid = False

        # 3️⃣ Email check
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, new_email):
            edit_email.error_text = "Please enter a valid email address"
            is_valid = False

        if not is_valid:
            page.update()
            return

        # Save if valid
        update_contact_db(db_conn, contact_id, new_name, new_phone, new_email)
        page.close(dialog)
        refresh_callback()
        _show_snackbar(page, "Contact updated successfully!")

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact", weight=ft.FontWeight.BOLD),
        content=ft.Column([edit_name, edit_phone, edit_email], spacing=10),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close(dialog)),
            ft.FilledButton("Save", icon=ft.Icons.SAVE, on_click=on_save),
        ],
    )

    page.dialog = dialog
    page.open(dialog)
    page.update()


# ---------------------- DELETE DIALOG ---------------------- #
def open_delete_confirmation(page: ft.Page, contact_id, db_conn, refresh_callback):
    """Show confirmation dialog for deleting a contact."""

    def confirm_delete(e):
        delete_contact_db(db_conn, contact_id)
        page.close(dialog)
        refresh_callback()
        _show_snackbar(page, "Contact deleted successfully!")

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete", weight=ft.FontWeight.BOLD),
        content=ft.Text("Are you sure you want to delete this contact? This action cannot be undone."),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.TextButton("No", on_click=lambda e: page.close(dialog)),
            ft.FilledButton("Yes, Delete", icon=ft.Icons.DELETE, on_click=confirm_delete),
        ],
    )

    page.dialog = dialog
    page.open(dialog)
    page.update()


# ---------------------- SNACKBAR HELPER ---------------------- #
def _show_snackbar(page: ft.Page, message: str):
    """Shows a snackbar message (for older Flet versions)."""
    page.snack_bar = ft.SnackBar(ft.Text(message))
    page.snack_bar.open = True
    page.update()
