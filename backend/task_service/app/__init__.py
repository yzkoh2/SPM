from flask import Flask
from flask_cors import CORS
from config import app_config
from .models import db
from .routes import task_bp
from .report import routes as reports_routes
import boto3

def create_app(config_name="development"):
    """Task Management Service Factory."""
    
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])

    if not app.config.get("TESTING"):
        app.s3_client = boto3.client(
            "s3",
            region_name=app.config['S3_REGION'],
            aws_access_key_id=app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=app.config['S3_SECRET_KEY']
        )
    else:
        app.s3_client = None
    
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