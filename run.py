import os
from app import create_app
from app.extensions import db

# Get environment
config_name = os.environ.get('FLASK_ENV', 'production')

# Create app
app = create_app(config_name)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    # For production, we'll use gunicorn in the Procfile
    # This is mainly for development and fallback
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
# This script initializes the Flask application and creates the necessary database tables.
# It also sets the application to run on a specified port and in debug mode if in development.