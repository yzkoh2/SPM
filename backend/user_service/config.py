import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local development.
load_dotenv()

class Config:
    """
    Base configuration class. Contains default settings and loads
    sensitive information from environment variables.
    """
    # A secret key is required by Flask for session management and security.
    # It should be a long, random string.
    SECRET_KEY = os.getenv('SECRET_KEY')

    # The database connection string.
    # This is loaded from the DATABASE_URL environment variable.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}

class TestingConfig(Config):
    """Configurations for Testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'

# A dictionary to access the different configuration classes.
app_config = {
    'development': Config,
    'testing': TestingConfig,
}