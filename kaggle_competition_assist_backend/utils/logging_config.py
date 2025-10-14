"""
Logging configuration for Kaggle Competition Assistant Backend
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(app):
    """
    Set up structured logging for the Flask application
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = app.config.get('LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Set logging level
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # Don't add handler if one already exists (prevents duplicate logs)
    if not app.logger.handlers:
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler with rotation (max 10MB, keep 5 files)
        log_file = app.config.get('LOG_FILE', './logs/kaggle_assist.log')
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
        
        # Add handlers to app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # Set level for werkzeug (Flask's WSGI server)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        # Log startup message
        app.logger.info("="*50)
        app.logger.info("Kaggle Competition Assistant Backend Started")
        app.logger.info(f"Environment: {app.config.get('ENV', 'development')}")
        app.logger.info(f"Debug Mode: {app.debug}")
        app.logger.info(f"Log Level: {log_level}")
        app.logger.info(f"Log File: {log_file}")
        app.logger.info("="*50)


def get_request_logger():
    """
    Get a logger specifically for request logging
    """
    return logging.getLogger('kaggle_assist.requests')


def get_agent_logger():
    """
    Get a logger specifically for agent operations
    """
    return logging.getLogger('kaggle_assist.agents')


def get_error_logger():
    """
    Get a logger specifically for errors
    """
    return logging.getLogger('kaggle_assist.errors')


def log_request(func):
    """
    Decorator to log API requests
    """
    def wrapper(*args, **kwargs):
        request_logger = get_request_logger()
        from flask import request
        
        # Log request details
        request_logger.info(f"API Request: {request.method} {request.path}")
        request_logger.info(f"Request Data: {request.get_json() if request.is_json else 'No JSON data'}")
        request_logger.info(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            request_logger.info(f"Request completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_logger = get_error_logger()
            error_logger.error(f"Request failed after {duration:.2f}s: {str(e)}")
            raise
    
    wrapper.__name__ = func.__name__
    return wrapper


