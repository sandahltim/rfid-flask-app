# refresh_logic.py
import requests
import sqlite3

def sanitize_string(value):
    return str(value).strip() if value is not None else ""

def refresh_data(db_path="inventory.db"):
    username = "api"
    password = "Broadway8101"
    login_url = "https://api.easyrfid.com/v1/login"
    data_url = "https://api.easyrfid.com/v1/items"

    login_payload = {"username": username, "password": password}
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=10, verify=False)
        login_response.raise_for_status()
        token = login_response.json().get("token")
        if not token:
            print("No token received in response")
            return
        print(f"Login successful, token: {token[:10]}...")
    except requests.exceptions.RequestException as e:
        print(f"Login failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(data_url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        all_items = response.json()
        print(f"Fetched {len(all_items)} items")
    except requests.exceptions.RequestException as e:
        print(f"Data fetch failed: {e}")
        return

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        for record in all_items:
            record["tag_id"] = sanitize_string(str(record.get("tag_id", "")))
            record["serial_number"] = sanitize_string(str(record.get("serial_number", "")))
            record["client_name"] = sanitize_string(str(record.get("client_name", "")))
            record["rental_class_num"] = sanitize_string(str(record.get("rental_class_num", "")))
            record["common_name"] = sanitize_string(str(record.get("common_name", "")))
            record["quality"] = sanitize_string(str(record.get("quality", "")))
            record["bin_location"] = sanitize_string(str(record.get("bin_location", "")))
            record["status"] = sanitize_string(str(record.get("status", "")))
            record["last_contract_num"] = sanitize_string(str(record.get("last_contract_num", "")))
            record["last_scanned_by"] = sanitize_string(str(record.get("last_scanned_by", "")))
            record["notes"] = sanitize_string(str(record.get("notes", "")))
            record["status_notes"] = sanitize_string(str(record.get("status_notes", "")))
            record["long"] = sanitize_string(str(record.get("long", "")))
            record["lat"] = sanitize_string(str(record.get("lat", "")))
            record["date_last_scanned"] = sanitize_string(str(record.get("date_last_scanned", "")))
            record["date_created"] = sanitize_string(str(record.get("date_created", "")))
            record["date_updated"] = sanitize_string(str(record.get("date_updated", "")))

            c.execute("""
                INSERT INTO items (
                    tag_id, serial_number, client_name, rental_class_num, common_name,
                    quality, bin_location, status, last_contract_num, last_scanned_by,
                    notes, status_notes, long, lat, date_last_scanned, date_created, date_updated
                )
                VALUES (
                    :tag_id, :serial_number, :client_name, :rental_class_num, :common_name,
                    :quality, :bin_location, :status, :last_contract_num, :last_scanned_by,
                    :notes, :status_notes, :long, :lat, :date_last_scanned, :date_created, :date_updated
                )
                ON CONFLICT(tag_id) DO UPDATE SET
                    serial_number=excluded.serial_number,
                    client_name=excluded.client_name,
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
        print("Data refresh complete")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    refresh_data()