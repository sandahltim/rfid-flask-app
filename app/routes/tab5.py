# app/routes/tab5.py
from flask import Blueprint, render_template
import sqlite3

tab5_bp = Blueprint('tab5', __name__, url_prefix="/tab5")

def get_db_connection():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_tab5_content():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        sql = """
        SELECT *
        FROM items
        WHERE status IN ('On Rent', 'Delivered')
          AND (UPPER(last_contract_num) LIKE 'L%' OR LOWER(client_name) = 'laundry')
        ORDER BY last_contract_num COLLATE NOCASE
        """
        c.execute(sql)
        rows = c.fetchall()
        columns = [desc[0] for desc in c.description]
        data = [dict(zip(columns, row)) for row in rows]
        conn.close()

        table_html = """
        <table id="tab5Table" class="table table-striped">
            <thead>
                <tr>
                    {% for column in columns %}
                        <th>{{ column }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                    <tr>
                        {% for column in columns %}
                            <td>{{ row[column] }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        """
        from flask import render_template_string
        return render_template_string(table_html, data=data, columns=columns)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "<p>Error loading Tab 5 data</p>"

@tab5_bp.route('/')
def tab5():
    return render_template('index.html', 
                          active_tab='tab5', 
                          tab1_html="", 
                          tab2_html="", 
                          tab3_html="", 
                          tab4_html="", 
                          tab5_html=get_tab5_content())