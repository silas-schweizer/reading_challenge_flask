import os
from werkzeug.security import generate_password_hash

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///reading_challenge.db'
    
    # API Configuration
    OPENLIBRARY_API_URL = os.environ.get('OPENLIBRARY_API_URL', 'https://openlibrary.org/search.json')
    
    # User credentials (in production, store hashed passwords)
    SILAS_PASSWORD_HASH = os.environ.get('SILAS_PASSWORD_HASH') or generate_password_hash('silas')
    NADINE_PASSWORD_HASH = os.environ.get('NADINE_PASSWORD_HASH') or generate_password_hash('nadine')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
