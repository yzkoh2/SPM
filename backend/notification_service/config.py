import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #Configuration for Notification Service
    SQLALCHEMY_DATABASE_URI = os.getenv('NOTIFICATION_DATABASE_URL','postgresql://user:user@notification_db:5432/notification_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Brevo SMTP Configuration
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp-relay.brevo.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')  
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')  
    
    # RabbitMQ Configuration 
    RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://admin:admin123@rabbitmq:5672/')
    
    # Other Microservices URLs
    USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://spm_user_service:6000')
    TASK_SERVICE_URL = os.getenv('TASK_SERVICE_URL', 'http://spm_task_service:6001')
    PROJECT_SERVICE_URL = os.getenv('PROJECT_SERVICE_URL', 'http://spm_project_service:6002')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False   