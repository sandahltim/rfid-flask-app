# app/routes/tab4.py
from flask import Blueprint, render_template
import sqlite3

tab4_bp = Blueprint("tab4_bp", __name__, url_prefix="/tab4")

def get_db_connection():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_tab4_content():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM items ORDER BY common_name").fetchall()
    conn.close()

    data = [dict(r) for r in rows]
    table_html = """
    <table id="tab4Table" class="table table-striped table-bordered dataTable">
      <thead>
        <tr>
          <th>Tag ID</th>
          <th>Serial Number</th>
          <th>Rental Class</th>
          <th>Common Name</th>
          <th>Status</th>
          <th>Last Contract</th>
          <th>Bin Location</th>
          <th>Quality</th>
          <th>Notes</th>
          <th>Last Scanned</th>
          <th>Created</th>
          <th>Updated</th>
        </tr>
      </thead>
      <tbody>
    """

    for item in data:
        table_html += f"""
        <tr>
          <td>{item.get('tag_id', '')}</td>
          <td>{item.get('serial_number', '')}</td>
          <td>{item.get('rental_class_num', '')}</td>
          <td>{item.get('common_name', '')}</td>
          <td>{item.get('status', '')}</td>
          <td>{item.get('last_contract_num', '')}</td>
          <td>{item.get('bin_location', '')}</td>
          <td>{item.get('quality', '')}</td>
          <td>{item.get('notes', '')}</td>
          <td>{item.get('date_last_scanned', '')}</td>
          <td>{item.get('date_created', '')}</td>
          <td>{item.get('date_updated', '')}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

@tab4_bp.route("/")
def show_tab4():
    return render_template(
        "index.html",
        tab1_html="",
        tab2_html="",
        tab3_html="",
        tab4_html=get_tab4_content(),
        tab5_html="",
        active_tab="tab4"
    )