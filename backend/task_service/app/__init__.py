from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .routes import task_bp
from .report import routes as reports_routes
import boto3

def create_app(config_name=None):
    """Task Management Service Factory."""
    
    app = Flask(__name__)
    
    if config_name == "testing":
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['S3_BUCKET_NAME'] = 'test-bucket'
        
        # Mock S3 client for testing
        app.s3_client = None  # Will be mocked in tests
        
        # Initialize database for testing
        db.init_app(app)
        
        # Register blueprint
        app.register_blueprint(task_bp, url_prefix="")
        
    else:
        app.config.from_object(Config)
        
        app.s3_client = boto3.client(
            "s3",
            region_name=app.config['S3_REGION'],
            aws_access_key_id=app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=app.config['S3_SECRET_KEY']
        )
        
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