# app/routes/tab3.py

import sqlite3
from flask import Blueprint, render_template
from collections import defaultdict

tab3_bp = Blueprint("tab3_bp", __name__, url_prefix="/tab3")

def get_db_connection():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def categorize_item(name):
    """Groups items by general category."""
    n = (name or "").lower()
    if 'tent' in n or 'canopy' in n or 'hp' in n or 'pole' in n:
        return 'Tent Tops'
    elif 'popcorn' in n or 'nacho' in n or 'cotton candy' in n or 'frozen' in n or 'machine' in n:
        return 'Concession'
    elif 'table' in n or 'plywood' in n or 'chair' in n or '4 prong' in n:
        return 'Tables and Chairs'
    elif 'round' in n:
        return 'Round Linen'
    elif '90x90' in n or '90x132' in n or '90x156' in n or '60x120' in n or '54 square' in n:
        return 'Rectangle Linen'
    else:
        return 'Other'

def needs_service(item):
    """
    Checks if an item requires service based on repair, cleaning, or inspection needs.
    Returns True if item qualifies for Tab 3.
    """
    # Cleaning-related issues
    cleaning_fields = ["dirty_or_mud", "leaves", "oil", "mold", "stain", "oxidation", "other"]
    
    # Repair-related issues
    repair_fields = ["rip_or_tear", "sewing_repair_needed", "grommet", "rope", "buckle"]

    # Any cleaning or repair flags marked as 1
    needs_cleaning = any(item.get(f, 0) == 1 for f in cleaning_fields)
    needs_repair = any(item.get(f, 0) == 1 for f in repair_fields)

    # Inspection required if 'inspect' or 'inspection' is in status_notes
    needs_inspection = "inspect" in (item.get("status_notes", "").lower())

    return needs_cleaning or needs_repair or needs_inspection

@tab3_bp.route("/")
def show_tab3():
    """
    Parent => [ +, Type, total_items ]
    Aggregates by common_name.
    Expands to full details of affected items.
    """
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM items").fetchall()
    conn.close()

    # Filter only items needing service
    data = [dict(r) for r in rows if needs_service(dict(r))]

    # Group by type
    type_map = defaultdict(list)
    for itm in data:
        t = categorize_item(itm.get("common_name",""))
        type_map[t].append(itm)

    # Build parent table
    tab3_html = build_type_parent_table(type_map)
    return render_template(
        "index.html",
        tab1_html="",
        tab2_html="",
        tab3_html=tab3_html,
        tab4_html="",
        active_tab="tab3"
    )

def build_type_parent_table(type_map):
    """
    3 columns => [ +, Type, total_items ]
    Expanding => Aggregated by common_name.
    """
    table_html = """
    <table id="tab3Table" class="table table-striped table-bordered">
      <thead>
        <tr>
          <th></th>
          <th>Type</th>
          <th>Total Items</th>
        </tr>
      </thead>
      <tbody>
    """

    for t, items_for_type in type_map.items():
        aggregator_html = build_name_aggregator_table(items_for_type)
        safe_agg = aggregator_html.replace('"','&quot;')

        table_html += f"""
        <tr data-child="{safe_agg}">
          <td class="dt-control">+</td>
          <td>{t}</td>
          <td>{len(items_for_type)}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

def build_name_aggregator_table(items):
    """
    Aggregator by name => 4 columns => [ +, common_name, repair_count, cleaning_count, inspection_count ]
    Expanding => full detail.
    """
    from collections import defaultdict
    cname_map = defaultdict(list)
    for itm in items:
        cname = itm.get("common_name","(No Name)")
        cname_map[cname].append(itm)

    table_html = """
    <table class='name-table table table-sm table-bordered'>
      <thead>
        <tr>
          <th></th>
          <th>Common Name</th>
          <th>Needs Repair</th>
          <th>Needs Cleaning</th>
          <th>Needs Inspection</th>
        </tr>
      </thead>
      <tbody>
    """
    for cname, sublist in cname_map.items():
        repair_count = sum(1 for itm in sublist if needs_service(itm) and any(itm.get(f, 0) == 1 for f in ["rip_or_tear", "sewing_repair_needed", "grommet", "rope", "buckle"]))
        cleaning_count = sum(1 for itm in sublist if needs_service(itm) and any(itm.get(f, 0) == 1 for f in ["dirty_or_mud", "leaves", "oil", "mold", "stain", "oxidation", "other"]))
        inspection_count = sum(1 for itm in sublist if needs_service(itm) and "inspect" in itm.get("status_notes", "").lower())

        detail_html = build_detail_table(sublist)
        safe_detail = detail_html.replace('"','&quot;')

        table_html += f"""
        <tr data-child2="{safe_detail}">
          <td class="dt-control2">+</td>
          <td>{cname}</td>
          <td>{repair_count}</td>
          <td>{cleaning_count}</td>
          <td>{inspection_count}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

def build_detail_table(items):
    """
    Final detail table with full columns.
    """
    table_html = """
    <table class='detail-table table table-sm table-striped'>
      <thead>
        <tr>
          <th>tag_id</th>
          <th>serial_number</th>
          <th>rental_class_num</th>
          <th>common_name</th>
          <th>status</th>
          <th>bin_location</th>
          <th>quality</th>
          <th>notes</th>
          <th>status_notes</th>
          <th>date_last_scanned</th>
        </tr>
      </thead>
      <tbody>
    """
    for itm in items:
        table_html += f"""
        <tr>
          <td>{itm.get('tag_id','')}</td>
          <td>{itm.get('serial_number','')}</td>
          <td>{itm.get('rental_class_num','')}</td>
          <td>{itm.get('common_name','')}</td>
          <td>{itm.get('status','')}</td>
          <td>{itm.get('bin_location','')}</td>
          <td>{itm.get('quality','')}</td>
          <td>{itm.get('notes','')}</td>
          <td>{itm.get('status_notes','')}</td>
          <td>{itm.get('date_last_scanned','')}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html
