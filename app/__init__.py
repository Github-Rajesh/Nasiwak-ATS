"""
Application Factory

This module contains the application factory pattern for creating Flask app instances.
It handles configuration loading, extension initialization, and blueprint registration.
"""

from flask import Flask
from app.config.settings import get_config
from app.extensions import init_extensions
from app.controllers import register_blueprints
from app.utils.error_handlers import register_error_handlers
import logging.config
import os
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

def create_app(config_name='development'):
    """
    Application factory function that creates and configures a Flask application.
    
    Args:
        config_name (str): Configuration environment name ('development', 'production', 'testing')
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Load environment variables first
    load_env_file()
    
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Ensure required directories exist
    _create_required_directories(app)
    
    # Setup logging
    _setup_logging(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Log application startup
    app.logger.info(f"RSART application created with config: {config_name}")
    
    return app

def _create_required_directories(app):
    """
    Create required directories if they don't exist.
    
    Args:
        app: Flask application instance
    """
    directories = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('JOB_DESCRIPTIONS_FOLDER'),
        app.config.get('LOG_FILE').parent if app.config.get('LOG_FILE') else None
    ]
    
    for directory in directories:
        if directory:
            directory.mkdir(parents=True, exist_ok=True)

def _setup_logging(app):
    """
    Setup application logging configuration.
    
    Args:
        app: Flask application instance
    """
    if app.config.get('LOGGING_CONFIG') and os.path.exists(app.config['LOGGING_CONFIG']):
        logging.config.fileConfig(app.config['LOGGING_CONFIG'])
    else:
        # Fallback logging configuration
        logging.basicConfig(
            level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )