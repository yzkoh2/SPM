import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    #Configuration class for Task Management Service
    #Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('TASK_DATABASE_URL')
    
    # Disable SQLAlchemy event system (not needed for this app)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}
    
    # Secret key for session management (if needed)
    SECRET_KEY = os.getenv('SECRET_KEY')

    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
    S3_REGION = os.getenv('S3_REGION')
    
    # RabbitMQ 
    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://admin:admin123@rabbitmq:5672/')
    
    # Debug mode (set to False in production)
    # DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # CORS Configuration
    # CORS_ORIGINS = [
    #     "http://localhost:5173",  # Frontend development server
    #     "http://localhost:8000",  # Kong gateway
    #     "http://frontend:5173"    # Docker frontend service
    # ]