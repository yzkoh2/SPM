from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import task_bp
import os  

def create_app():
    """Task Management Service Factory."""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    # Create upload directories if they don't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(os.path.join(upload_folder, 'tasks'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'subtasks'), exist_ok=True)
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