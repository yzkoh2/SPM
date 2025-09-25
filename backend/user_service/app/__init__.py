from flask import Flask
from flask_cors import CORS
from config import app_config
from .models import db
from .routes import user_bp

def create_app(config_name="development"):
    """An application factory."""
    
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    db.init_app(app)
    app.register_blueprint(user_bp)

    return app