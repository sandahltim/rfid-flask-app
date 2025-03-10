# app/routes/tab5.py

import sqlite3
from flask import Blueprint, render_template
from collections import defaultdict

tab5_bp = Blueprint("tab5_bp", __name__, url_prefix="/tab5")

def get_db_connection():
    """Opens a local SQLite connection with row_factory=sqlite3.Row."""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_contract_date(items):
    """
    Returns the earliest 'date_updated' among these items.
    This represents when the contract was set to On Rent or Delivered.
    If you want the latest date, swap min(...) with max(...).
    """
    dates = []
    for itm in items:
        dt = itm.get("date_updated","")
        if dt:
            dates.append(dt)
    if not dates:
        return ""
    return min(dates)  # or max(dates) if you prefer

@tab5_bp.route("/")
def show_tab5():
    """
    Tab 5: Linens at laundry. 
    Contract # starts with 'L' OR client_name='laundry' (case-insensitive),
    status is 'On Rent' or 'Delivered'.
    
    Parent table: [ +, Contract#, Client Name, Date On/Delivered ]
    Child table: [ Common Name, Status, Date Updated, Last Scanned By, Notes ]
    """
    conn = get_db_connection()
    sql = """
    SELECT *
    FROM items
    WHERE (status IN ('On Rent','Delivered'))
      AND (
           LOWER(client_name)='laundry'
           OR UPPER(last_contract_num) LIKE 'L%'
          )
    ORDER BY last_contract_num COLLATE NOCASE
    """
    rows = conn.execute(sql).fetchall()
    conn.close()

    data = [dict(r) for r in rows]

    # Group items by contract number
    contract_map = defaultdict(list)
    for itm in data:
        cnum = itm.get("last_contract_num","UNKNOWN")
        contract_map[cnum].append(itm)

    # Build the parent table
    tab5_html = build_parent_table(contract_map)

    return render_template(
        "index.html",
        tab1_html="",
        tab2_html="",
        tab3_html="",
        tab4_html="",
        tab5_html=tab5_html,
        active_tab="tab5"
    )

def build_parent_table(contract_map):
    """
    Parent table columns: [ +, Contract#, Client Name, Date On/Delivered ]
    Expand => child table of items
    """
    table_html = """
    <table id="tab5Table" class="table table-striped table-bordered">
      <thead>
        <tr>
          <th></th>
          <th>Contract #</th>
          <th>Client Name</th>
          <th>Date On/Delivered</th>
        </tr>
      </thead>
      <tbody>
    """

    for cnum, items in contract_map.items():
        # We'll assume all items in a contract share the same client_name
        # or pick the first one
        client_name = items[0].get("client_name","Unknown") if items else "Unknown"

        # earliest date_updated
        contract_date = get_contract_date(items)

        # child table for items
        child_html = build_child_table(items)
        safe_child = child_html.replace('"','&quot;')

        table_html += f"""
        <tr data-child="{safe_child}">
          <td class="dt-control">+</td>
          <td>{cnum}</td>
          <td>{client_name}</td>
          <td>{contract_date}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

def build_child_table(items):
    """
    Child table columns: [ Common Name, Status, Date Updated, Last Scanned By, Notes ]
    """
    table_html = """
    <table class='table table-sm table-bordered'>
      <thead>
        <tr>
          <th>Common Name</th>
          <th>Status</th>
          <th>Date Updated</th>
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
          <td>{itm.get('date_updated','')}</td>
          <td>{itm.get('last_scanned_by','')}</td>
          <td>{itm.get('notes','')}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html
