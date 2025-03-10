# app/__init__.py
import os
import time
import threading
from flask import Flask
from db_utils import initialize_db
from refresh_logic import refresh_data

DB_PATH = "inventory.db"

def create_app():
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "templates")

    app = Flask(__name__, template_folder=template_path)

    initialize_db(DB_PATH)

    def bg_refresh():
        while True:
            try:
                refresh_data(DB_PATH)
            except Exception as e:
                print(f"Background refresh failed: {e}")
            time.sleep(600)  # Refresh every 10 minutes

    t = threading.Thread(target=bg_refresh, daemon=True)
    t.start()

    from app.routes.root import root_bp
    from app.routes.tab1 import tab1_bp
    from app.routes.tab2 import tab2_bp
    from app.routes.tab3 import tab3_bp
    from app.routes.tab4 import tab4_bp
    from app.routes.tab5 import tab5_bp

    app.register_blueprint(root_bp, url_prefix='')
    app.register_blueprint(tab1_bp, url_prefix='/tab1')
    app.register_blueprint(tab2_bp, url_prefix='/tab2')
    app.register_blueprint(tab3_bp, url_prefix='/tab3')
    app.register_blueprint(tab4_bp, url_prefix='/tab4')
    app.register_blueprint(tab5_bp, url_prefix='/tab5')

    return app