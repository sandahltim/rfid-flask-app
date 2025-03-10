# db_utils.py

import sqlite3

def initialize_db(db_path="inventory.db"):
    """
    Creates (if not exists) the SQLite database and tables for items.
    Adjust columns to match the API fields you plan to store.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Based on the Item Master Data from your API docs, we include columns like:
    #   tag_id, serial_number, rental_class_num, common_name, quality, bin_location,
    #   status, last_contract_num, last_scanned_by, notes, status_notes,
    #   long, lat, date_last_scanned, date_created, date_updated
    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        tag_id TEXT PRIMARY KEY,
        serial_number TEXT,
        rental_class_num TEXT,
        common_name TEXT,
        quality TEXT,
        bin_location TEXT,
        status TEXT,
        last_contract_num TEXT,
        last_scanned_by TEXT,
        notes TEXT,
        status_notes TEXT,
        long TEXT,
        lat TEXT,
        date_last_scanned TEXT,
        date_created TEXT,
        date_updated TEXT
    );
    """)

    # If you have other tables (e.g., transactions), create them here similarly.

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")
