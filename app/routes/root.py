# app/routes/root.py
from flask import Blueprint, render_template

root_bp = Blueprint("root_bp", __name__)

@root_bp.route("/")
def root_home():
    """
    Shows the nav tabs from index.html at http://localhost:5000/.
    No specific tab content is filled here, so we pass empty placeholders.
    """
    return render_template(
        "index.html",
        tab1_html="",
        tab2_html="",
        tab3_html="",
        tab4_html="",
        active_tab="root"
    )
