import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'authentication-secret-key-2026'
    
    # MongoDB Configuration
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/authentication'
    
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
    # Facial Geometry Template Matching (normalized landmark positions and measurements)
    # Compares geometric structure - lighting invariant and pose tolerant
    # Similarity score between 0 and 1 (1 = identical geometry)
    # Accuracy threshold for authentication: 90% (0-100)
    # - 90% = balanced: rejects different people, accepts same person with head rotation/scale variation
    # - Higher (95%+) = stricter, fewer false positives but more false negatives
    # - Lower (80%+) = more lenient, fewer false negatives but more false positives
    FACE_RECOGNITION_ACCURACY_THRESHOLD = 90  # Required accuracy percentage for authentication
    FACE_RECOGNITION_TOLERANCE = 0.25  # Legacy tolerance (0.15-0.35, lower = stricter)
    FACE_RECOGNITION_MODEL = 'facial_geometry'  # Geometric template matching
    
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
    MONGO_URI = 'mongodb://localhost:27017/authentication_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
