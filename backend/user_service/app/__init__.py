from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import user_bp # Assuming user_bp is your Blueprint from routes.py

def create_app():
    """An application factory."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(user_bp)

    return app