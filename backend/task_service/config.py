import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Task Management Service"""
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TASK_DATABASE_URL', 
        'postgresql://task_user:task_pass@task_db:5432/task_db'
    )
    
    # Disable SQLAlchemy event system (not needed for this app)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management (if needed)
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # JWT Configuration (if using JWT)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    
    # Debug mode (set to False in production)
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:5173",  # Frontend development server
        "http://localhost:8000",  # Kong gateway
        "http://frontend:5173"    # Docker frontend service
    ]