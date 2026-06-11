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
    # OpenCV-based feature matching using ORB keypoints and histogram analysis
    # Euclidean distance between normalized feature vectors (0 = identical, ~2 = completely different)
    # Recommended range: 0.25-0.45 (lower = stricter)
    # 0.35 = balanced: rejects different people, accepts same person with pose/lighting variation
    FACE_RECOGNITION_TOLERANCE = 0.35
    FACE_RECOGNITION_MODEL = 'opencv'  # OpenCV-based feature matching
    
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
