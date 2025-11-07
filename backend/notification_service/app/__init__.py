from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .rabbitmq_consumer import start_consumer_thread
from .scheduler import start_notification_scheduler
import os

consumer = None
scheduler = None

def create_app(config_name=None):
    app = Flask(__name__)
    
    #Configure based on environment
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        #Set dummy values for required configs
        app.config['SMTP_HOST'] = 'localhost'
        app.config['SMTP_PORT'] = 587
        app.config['SMTP_USERNAME'] = 'test'
        app.config['SMTP_PASSWORD'] = 'test'
        app.config['SMTP_FROM_EMAIL'] = 'test@test.com'
        app.config['RABBITMQ_URL'] = 'amqp://test'
        app.config['USER_SERVICE_URL'] = 'http://test'
        app.config['TASK_SERVICE_URL'] = 'http://test'
        app.config['PROJECT_SERVICE_URL'] = 'http://test'
    else:
        app.config.from_object(Config)
    
    #Initialize database
    db.init_app(app)
    
    #Create tables if they don't exist
    with app.app_context():
        db.create_all()
        if not app.config.get('TESTING'):
            print("✅ Database tables created/verified")
    
    #Enable CORS
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:8000"])
    
    if not app.config.get('TESTING'):
        print("✅ Notification Service initialized")
    
    #Start background services only in production
    if not app.config.get('TESTING') and os.environ.get('WERKZEUG_RUN_MAIN') != 'false':
        global consumer, scheduler
        consumer = start_consumer_thread(app)
        scheduler = start_notification_scheduler(app)

    return app