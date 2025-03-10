# refresh_logic.py

import sqlite3
import requests

def sanitize_string(s):
    """
    Removes single quotes (') and double quotes (") from a string.
    Add or remove logic here if you want to strip other punctuation.
    """
    return s.replace("'", "").replace('"', "")

def refresh_data(db_path="inventory.db"):
    """
    Fetch data from the API, sanitize fields by removing quotes,
    then upsert into the 'items' table. Called periodically by
    the background thread in app/__init__.py.
    """
    print("Refreshing data from the real API...")

    # 1) Log in to get an access token (example credentials)
    LOGIN_URL = "https://login.cloud.ptshome.com/api/v1/login"
    login_payload = {"username": "api", "password": "Broadway8101"}
    login_headers = {"Content-Type": "application/json"}

    try:
        login_resp = requests.post(LOGIN_URL, json=login_payload, headers=login_headers, timeout=10)
        login_resp.raise_for_status()
        token = login_resp.json().get("access_token")
        if not token:
            print("No access_token returned; cannot proceed.")
            return
    except Exception as e:
        print("Error logging in:", e)
        return

    # 2) Fetch all items in chunks (limit=200) to ensure we get everything
    ITEM_MASTER_URL = "https://cs.iot.ptshome.com/api/v1/data/14223767938169344381"
    master_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    offset = 0
    limit = 200
    all_items = []

    while True:
        params = {"limit": limit, "offset": offset}
        try:
            resp = requests.get(ITEM_MASTER_URL, headers=master_headers, params=params, timeout=10)
            resp.raise_for_status()
            data_chunk = resp.json().get("data", [])
            if not data_chunk:
                break
            all_items.extend(data_chunk)
            offset += limit
        except Exception as e:
            print("Error fetching items chunk:", e)
            return

    print(f"Fetched {len(all_items)} total items. Sanitizing and upserting into SQLite...")

    # 3) Upsert into the 'items' table
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        for record in all_items:
            # Sanitize relevant string fields before insertion
            record["tag_id"] = sanitize_string(str(record.get("tag_id","")))
            record["serial_number"] = sanitize_string(str(record.get("serial_number","")))
            record["rental_class_num"] = sanitize_string(str(record.get("rental_class_num","")))
            record["common_name"] = sanitize_string(str(record.get("common_name","")))
            record["quality"] = sanitize_string(str(record.get("quality","")))
            record["bin_location"] = sanitize_string(str(record.get("bin_location","")))
            record["status"] = sanitize_string(str(record.get("status","")))
            record["last_contract_num"] = sanitize_string(str(record.get("last_contract_num","")))
            record["last_scanned_by"] = sanitize_string(str(record.get("last_scanned_by","")))
            record["notes"] = sanitize_string(str(record.get("notes","")))
            record["status_notes"] = sanitize_string(str(record.get("status_notes","")))
            record["long"] = sanitize_string(str(record.get("long","")))
            record["lat"] = sanitize_string(str(record.get("lat","")))
            record["date_last_scanned"] = sanitize_string(str(record.get("date_last_scanned","")))
            record["date_created"] = sanitize_string(str(record.get("date_created","")))
            record["date_updated"] = sanitize_string(str(record.get("date_updated","")))

            c.execute("""
                INSERT INTO items (
                    tag_id,
                    serial_number,
                    rental_class_num,
                    common_name,
                    quality,
                    bin_location,
                    status,
                    last_contract_num,
                    last_scanned_by,
                    notes,
                    status_notes,
                    long,
                    lat,
                    date_last_scanned,
                    date_created,
                    date_updated
                )
                VALUES (
                    :tag_id,
                    :serial_number,
                    :rental_class_num,
                    :common_name,
                    :quality,
                    :bin_location,
                    :status,
                    :last_contract_num,
                    :last_scanned_by,
                    :notes,
                    :status_notes,
                    :long,
                    :lat,
                    :date_last_scanned,
                    :date_created,
                    :date_updated
                )
                ON CONFLICT(tag_id) DO UPDATE SET
                    serial_number=excluded.serial_number,
                    rental_class_num=excluded.rental_class_num,
                    common_name=excluded.common_name,
                    quality=excluded.quality,
                    bin_location=excluded.bin_location,
                    status=excluded.status,
                    last_contract_num=excluded.last_contract_num,
                    last_scanned_by=excluded.last_scanned_by,
                    notes=excluded.notes,
                    status_notes=excluded.status_notes,
                    long=excluded.long,
                    lat=excluded.lat,
                    date_last_scanned=excluded.date_last_scanned,
                    date_created=excluded.date_created,
                    date_updated=excluded.date_updated
            """, record)

        conn.commit()
        print("Data refresh complete (quotes stripped).")
    except Exception as e:
        print("Error updating data in SQLite:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
