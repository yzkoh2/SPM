from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import task_bp

def create_app():
    """Task Management Service Factory."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend communication
    CORS(app, origins=["http://localhost:5173", "http://localhost:8000"])
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprint - Use prefix="" because Kong routes /tasks to this service
    app.register_blueprint(task_bp, url_prefix="")
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    return app