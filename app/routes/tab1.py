# app/routes/tab1.py

from flask import Blueprint, render_template
import sqlite3
from collections import defaultdict

tab1_bp = Blueprint("tab1_bp", __name__, url_prefix="/tab1")

def get_db_connection():
    """Opens local SQLite with row_factory=sqlite3.Row."""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

@tab1_bp.route("/")
def show_tab1():
    """
    Tab 1: Shows 'Open Contracts' or 'Delivered' items,
    grouped by contract number, expandable to see each item.
    Sortable & searchable with DataTables in index.html
    """
    conn = get_db_connection()
    # Only items with status 'On Rent' or 'Delivered', ignoring empty contract nums
    sql = """
    SELECT *
    FROM items
    WHERE (status='On Rent' OR status='Delivered')
      AND last_contract_num != ''
    ORDER BY last_contract_num COLLATE NOCASE
    """
    rows = conn.execute(sql).fetchall()
    conn.close()

    data = [dict(r) for r in rows]

    # Group by contract number
    contract_map = defaultdict(list)
    for itm in data:
        cnum = itm.get("last_contract_num", "UNKNOWN")
        contract_map[cnum].append(itm)

    # Build the parent table HTML
    tab1_html = build_contract_table(contract_map)

    return render_template(
        "index.html",
        tab1_html=tab1_html,
        tab2_html="",
        tab3_html="",
        tab4_html="",
        active_tab="tab1"
    )

def build_contract_table(contract_map):
    """
    Parent table: [ +, Contract#, ClientName ]
    Expand => child table of items
    """
    table_html = """
    <table id="tab1Table" class="table table-striped table-bordered">
      <thead>
        <tr>
          <th></th>
          <th>Contract #</th>
          <th>Client Name</th>
        </tr>
      </thead>
      <tbody>
    """

    for contract_num, items in contract_map.items():
        # We'll assume all items in a contract share the same client_name
        # or pick the first one
        client_name = items[0].get("client_name", "Unknown") if items else "Unknown"

        # Build child table of items
        child_html = build_items_table(items)
        safe_child = child_html.replace('"', '&quot;')

        table_html += f"""
        <tr data-child="{safe_child}">
          <td class="dt-control">+</td>
          <td>{contract_num}</td>
          <td>{client_name}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

def build_items_table(items):
    """
    Child table: shows items under this contract
    [ Common Name, Status, Last Scanned, Scanned By, Notes ]
    """
    table_html = """
    <table class='table table-sm table-bordered'>
      <thead>
        <tr>
          <th>Common Name</th>
          <th>Status</th>
          <th>Date Last Scanned</th>
          <th>Last Scanned By</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
    """
    for itm in items:
        table_html += f"""
        <tr>
          <td>{itm.get('common_name','')}</td>
          <td>{itm.get('status','')}</td>
          <td>{itm.get('date_last_scanned','')}</td>
          <td>{itm.get('last_scanned_by','')}</td>
          <td>{itm.get('notes','')}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html
