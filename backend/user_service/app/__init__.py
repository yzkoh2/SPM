from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import user_bp # Assuming user_bp is your Blueprint from routes.py

def create_app():
    """An application factory."""
    app = Flask(__name__)

    CORS(app)

    # 1. Load the configuration from the config.py file.
    app.config.from_object(Config)

    # 2. Initialize extensions like the database.
    db.init_app(app)

    # 3. Register your blueprints (which contain your routes).
    app.register_blueprint(user_bp)

    return app