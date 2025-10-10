from flask import Flask
from flask_cors import CORS
from config import Config
from .rabbitmq_consumer import start_consumer_thread
import os

consumer = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    #Enable CORS
    CORS(app, origins=["http://localhost:5173", "http://localhost:8000"])
    
    print("✅ Notification Service initialized")
    
    #Start RabbitMQ consumer in background thread
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        global consumer
        consumer = start_consumer_thread(app)
    
    return app