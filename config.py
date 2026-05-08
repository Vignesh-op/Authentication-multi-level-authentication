import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'authsafe-secret-key-2026'
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/authsafe'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
    CARDS_FOLDER = os.path.join(os.path.dirname(__file__), 'static/cards')
    
    # Face Recognition Configuration
    # Cosine distance between normalized vectors is in roughly the 0..2 range (lower = stricter).
    FACE_RECOGNITION_TOLERANCE = 0.85
    FACE_RECOGNITION_MODEL = 'hog'  # 'hog' is faster, 'cnn' is more accurate
    
    # QR Code Configuration
    QR_CODE_SIZE = 10
    
    # Ensure upload folders exist
    def __init__(self):
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.CARDS_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/authsafe_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
