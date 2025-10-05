import sqlite3
import os


def init_db():
    """
    Initializes the database and creates the contacts table if it doesn't exist.
    The database is saved inside a 'data' folder within your app directory.
    """
    # Determine where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a "data" subfolder inside the app directory if it doesn't exist
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # Database file path: contact_book_app/data/contacts.db
    db_path = os.path.join(data_dir, "contacts.db")

    # Connect to the SQLite database (creates it if missing)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # Create the contacts table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')

    conn.commit()
    return conn


def add_contact_db(conn, name, phone, email):
    """Adds a new contact to the database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
        (name, phone, email)
    )
    conn.commit()
    return cursor.lastrowid


def get_all_contacts_db(conn, search: str | None = None):
    """
    Retrieves all contacts from the database.
    If a search term is provided, filters by name, phone, or email.
    """
    cursor = conn.cursor()
    if search and search.strip():
        query = f"%{search.strip()}%"
        cursor.execute(
            "SELECT id, name, phone, email FROM contacts "
            "WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? "
            "ORDER BY name",
            (query, query, query),
        )
    else:
        cursor.execute("SELECT id, name, phone, email FROM contacts ORDER BY name")
    return cursor.fetchall()


def update_contact_db(conn, contact_id, name, phone, email):
    """Updates an existing contact."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
        (name, phone, email, contact_id)
    )
    conn.commit()
    return cursor.rowcount


def delete_contact_db(conn, contact_id):
    """Deletes a contact from the database."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    return cursor.rowcount
