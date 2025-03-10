# app/routes/tab2.py
import sqlite3
import re
import string
from flask import Blueprint, render_template
from collections import defaultdict

tab2_bp = Blueprint("tab2_bp", __name__, url_prefix="/tab2")

EXTENDED_COLORS = {
    "white", "black", "red", "blue", "green", "yellow", "purple", "brown",
    "orange", "pink", "gray", "grey", "silver", "gold", "beige", "maroon",
    "navy", "teal", "lime", "olive", "cyan", "magenta", "turquoise",
    "lavender", "peach", "coral", "tan", "burgundy", "bronze", "khaki",
    "ivory", "cream", "mustard", "rust", "charcoal", "indigo", "violet",
    "fuchsia", "plum", "mint", "sage", "orchid", "apricot", "amber", "auburn",
    "emerald", "jade", "chocolate", "sky", "royal", "coffee", "sand", "eggplant",
    "denim", "rose", "mauve", "periwinkle", "chartreuse", "forest", "scarlet",
    "golden", "salmon", "raspberry", "beet", "ruby", "sepia", "smoke", "ash"
}

def get_db_connection():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def strip_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)

def parse_color(common_name):
    raw = (common_name or "").lower()
    stripped = strip_punctuation(raw)
    tokens = stripped.split()
    for t in tokens:
        if t in EXTENDED_COLORS:
            return t.capitalize()
    return "NoColor"

def tokenize_for_category(name):
    n = (name or "").lower()
    tokens = re.split(r'[^a-z0-9]+', n)
    return [t for t in tokens if t]

def categorize_item(name):
    tokens = tokenize_for_category(name)
    if any(t in tokens for t in ['table', 'plywood', 'chair']) or ('4' in tokens and 'prong' in tokens):
        return 'Tables and Chairs'
    if any(t in tokens for t in ['tent', 'canopy', 'hp', 'pole', 'navi', 'ncp']):
        return 'Tent Tops'
    if any(t in tokens for t in ['90x90', '90x132', '90x156', '60x120']) or ('54' in tokens and 'square' in tokens):
        return 'Rectangle Linen'
    if 'round' in tokens:
        return 'Round Linen'
    if any(t in tokens for t in ['popcorn', 'nacho', 'frozen', 'machine', 'hotdog']):
        return 'Concession'
    if 'cotton' in tokens and 'candy' in tokens:
        return 'Concession'
    return 'Other'

def get_tab2_content():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM items").fetchall()
    conn.close()

    data = [dict(r) for r in rows]
    type_map = defaultdict(list)
    for itm in data:
        t = categorize_item(itm.get("common_name", ""))
        type_map[t].append(itm)

    return build_type_parent_table(type_map)

@tab2_bp.route("/")
def show_tab2():
    return render_template(
        "index.html",
        tab1_html="",
        tab2_html=get_tab2_content(),
        tab3_html="",
        tab4_html="",
        tab5_html="",
        active_tab="tab2"
    )

def build_type_parent_table(type_map):
    table_html = """
    <label for="colorFilter">Filter Linens by Color:</label>
    <select id="colorFilter">
      <option value="">All Colors</option>
    """
    for color in sorted(EXTENDED_COLORS):
        table_html += f'<option value="{color}">{color.capitalize()}</option>'
    table_html += "</select>"

    table_html += """
    <table id="tab2Table" class="table table-striped table-bordered">
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
        safe_agg = aggregator_html.replace('"', '"')

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
    cname_map = defaultdict(list)
    for itm in items:
        cname = itm.get("common_name", "(No Name)")
        cname_map[cname].append(itm)

    table_html = """
    <table class='name-table table table-sm table-bordered' data-colcount='5'>
      <thead>
        <tr>
          <th></th>
          <th>Common Name</th>
          <th>On Rent</th>
          <th>Ready</th>
          <th>Other</th>
        </tr>
      </thead>
      <tbody>
    """

    for cname, sublist in cname_map.items():
        on_rent = sum(1 for itm in sublist if itm.get("status", "").lower() == "on rent")
        ready = sum(1 for itm in sublist if itm.get("status", "").lower() in ("", "ready to rent"))
        other = len(sublist) - on_rent - ready

        detail_html = build_detail_table(sublist)
        safe_detail = detail_html.replace('"', '"')

        table_html += f"""
        <tr data-child2="{safe_detail}">
          <td class="dt-control2">+</td>
          <td>{cname}</td>
          <td>{on_rent}</td>
          <td>{ready}</td>
          <td>{other}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

def build_detail_table(items):
    table_html = """
    <table class='detail-table table table-sm table-striped' data-colcount='13'>
      <thead>
        <tr>
          <th>tag_id</th>
          <th>serial_number</th>
          <th>rental_class_num</th>
          <th>common_name</th>
          <th>status</th>
          <th>last_contract_num</th>
          <th>bin_location</th>
          <th>quality</th>
          <th>notes</th>
          <th>status_notes</th>
          <th>date_last_scanned</th>
          <th>date_created</th>
          <th>date_updated</th>
        </tr>
      </thead>
      <tbody>
    """
    for itm in items:
        table_html += f"""
        <tr>
          <td>{itm.get('tag_id', '')}</td>
          <td>{itm.get('serial_number', '')}</td>
          <td>{itm.get('rental_class_num', '')}</td>
          <td>{itm.get('common_name', '')}</td>
          <td>{itm.get('status', '')}</td>
          <td>{itm.get('last_contract_num', '')}</td>
          <td>{itm.get('bin_location', '')}</td>
          <td>{itm.get('quality', '')}</td>
          <td>{itm.get('notes', '')}</td>
          <td>{itm.get('status_notes', '')}</td>
          <td>{itm.get('date_last_scanned', '')}</td>
          <td>{itm.get('date_created', '')}</td>
          <td>{itm.get('date_updated', '')}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html