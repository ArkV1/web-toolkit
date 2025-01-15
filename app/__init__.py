from flask import Flask
from flask_socketio import SocketIO
from app.core.config import Config
import os
import logging
from logging.handlers import FileHandler

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

def setup_logging(app):
    """Configure logging for the application"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Configure file handlers
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    
    # Error log
    error_handler = FileHandler('logs/error.log')
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Access log
    access_handler = FileHandler('logs/access.log')
    access_handler.setFormatter(file_formatter)
    access_handler.setLevel(logging.INFO)
    
    # App log
    app_handler = FileHandler('logs/app.log')
    app_handler.setFormatter(file_formatter)
    app_handler.setLevel(logging.INFO)
    
    # Add handlers to app logger
    app.logger.addHandler(error_handler)
    app.logger.addHandler(access_handler)
    app.logger.addHandler(app_handler)
    app.logger.setLevel(logging.INFO)

def cleanup_logs(app):
    """Clean up log files on startup"""
    log_files = ['logs/error.log', 'logs/access.log', 'logs/app.log']
    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write('')  # Clear the file
                app.logger.info(f"Cleaned up log file: {log_file}")
        except Exception as e:
            app.logger.error(f"Error cleaning log file {log_file}: {str(e)}")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    socketio.init_app(app)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Set up logging
    setup_logging(app)

    # Clean up logs on startup
    cleanup_logs(app)

    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app 