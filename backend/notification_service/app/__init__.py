from flask import Flask
from flask_cors import CORS
from config import Config
from .models import db
from .rabbitmq_consumer import start_consumer_thread
from .scheduler import start_deadline_scheduler
import os

consumer = None
scheduler = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    #Initialize database
    db.init_app(app)
    
    #Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    #Enable CORS
    CORS(app, origins=["http://localhost:5173", "http://localhost:8000"])
    
    print("✅ Notification Service initialized")
    
    #Start background services
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        global consumer, scheduler
        
        #Start RabbitMQ consumer for status updates
        consumer = start_consumer_thread(app)
        
        #Start deadline reminder scheduler
        scheduler = start_deadline_scheduler(app)
        
    return app