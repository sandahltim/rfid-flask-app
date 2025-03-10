# db_utils.py
import sqlite3

def initialize_db(db_path="inventory.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        tag_id TEXT PRIMARY KEY,
        serial_number TEXT,
        client_name TEXT,
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

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    initialize_db()