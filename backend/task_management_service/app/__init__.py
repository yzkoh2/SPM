from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import task_bp # Assuming task_bp is your Blueprint from routes.py

def create_app():
    """Task Management Service Factory."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    app.register_blueprint(task_bp, url_prefix="/tasks")

    return app