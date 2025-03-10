# app/__init__.py

import os
import time
import threading
from flask import Flask
from db_utils import initialize_db
from refresh_logic import refresh_data

DB_PATH = "inventory.db"

def create_app():
    """
    Initializes the Flask app, registers blueprints (routes), 
    and starts a background thread to refresh data every 10 minutes.
    """
    # Ensure template path is set correctly
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "..", "templates")

    # Initialize Flask application
    app = Flask(__name__, template_folder=template_path)

    # Initialize the database
    initialize_db(DB_PATH)

    # Background refresh thread
    def bg_refresh():
        while True:
            refresh_data(DB_PATH)
            time.sleep(600)  # Refresh every 10 minutes

    t = threading.Thread(target=bg_refresh, daemon=True)
    t.start()

    # Import and register your blueprints (tabs)
    from app.routes.root import root_bp
    from app.routes.tab1 import tab1_bp
    from app.routes.tab2 import tab2_bp
    from app.routes.tab3 import tab3_bp  # Tab 3: Needs Service
    from app.routes.tab4 import tab4_bp  # Tab 4: Full Inventory
    from app.routes.tab5 import tab5_bp  # Tab 5: Laundry Linens (new)

    # Register blueprints
    app.register_blueprint(root_bp)
    app.register_blueprint(tab1_bp)
    app.register_blueprint(tab2_bp)
    app.register_blueprint(tab3_bp)  # Ensure Tab 3 is registered
    app.register_blueprint(tab4_bp)  # Ensure Tab 4 is registered
    app.register_blueprint(tab5_bp)  # Register Tab 5

    return app

