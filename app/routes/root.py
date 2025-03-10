# app/routes/root.py
from flask import Blueprint, render_template
from app.routes.tab1 import get_tab1_content
from app.routes.tab2 import get_tab2_content
from app.routes.tab3 import get_tab3_content
from app.routes.tab4 import get_tab4_content
from app.routes.tab5 import get_tab5_content

root_bp = Blueprint('root', __name__)

@root_bp.route('/')
def index():
    return render_template('index.html', 
                          active_tab=None, 
                          tab1_html="", 
                          tab2_html="", 
                          tab3_html="", 
                          tab4_html="", 
                          tab5_html="")