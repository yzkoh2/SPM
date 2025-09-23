from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import task_bp

def create_app():
    """Task Management Service Factory."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure CORS for development
    CORS(app, origins=['http://localhost:5173'], supports_credentials=True)

    db.init_app(app)
    app.register_blueprint(task_bp, url_prefix="/tasks")

    return app