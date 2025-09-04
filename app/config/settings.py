import os
from pathlib import Path

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # File handling - Use absolute paths
    BASE_DIR = Path(__file__).parent.parent.parent  # Go up from app/config to project root
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploaded_resumes'
    JOB_DESCRIPTIONS_FOLDER = BASE_DIR / 'data' / 'job_descriptions'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # Database - Default to SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///rsart.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Cache
    CACHE_TYPE = 'redis' if os.environ.get('REDIS_URL') else 'simple'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # Logging
    LOGGING_CONFIG = Path('app/config/logging.conf')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = Path('logs/rsart.log')
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Resume processing
    TOP_CANDIDATES_COUNT = int(os.environ.get('TOP_CANDIDATES_COUNT', 10))
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.1))
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')  # Cost-effective model
    USE_AI_MATCHING = os.environ.get('USE_AI_MATCHING', 'True').lower() == 'true'

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    # Use SQLite for development by default
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///rsart.db')
    CACHE_TYPE = 'simple'  # Use simple cache for development

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database URL is required in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Additional production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }

class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = 'simple'

def get_config(config_name):
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    # Validate production configuration only when it's actually requested
    if config_name == 'production':
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("No SECRET_KEY set for production environment")
        if not os.environ.get('DATABASE_URL'):
            raise ValueError("No DATABASE_URL set for production environment")
    
    return config_map.get(config_name, DevelopmentConfig)