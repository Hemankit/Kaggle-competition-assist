#!/usr/bin/env python3
"""
Test logging configuration and utilities
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add the backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kaggle_competition_assist_backend'))

def test_logging_config():
    """Test logging configuration setup"""
    print("🧪 Testing Logging Configuration")
    print("=" * 40)
    
    try:
        # Test imports
        from utils.logging_config import setup_logging, get_request_logger, get_agent_logger, get_error_logger, log_request
        print("✅ Logging imports successful")
        
        # Test logger creation
        request_logger = get_request_logger()
        agent_logger = get_agent_logger()
        error_logger = get_error_logger()
        
        print("✅ Logger creation successful")
        
        # Test log messages
        request_logger.info("Test request log message")
        agent_logger.info("Test agent log message")
        error_logger.warning("Test error log message")
        
        print("✅ Log message writing successful")
        
        # Test decorator
        @log_request
        def test_function():
            return "Test response"
        
        result = test_function()
        print(f"✅ Log decorator test successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging configuration test failed: {str(e)}")
        return False

def test_flask_logging():
    """Test Flask app logging setup"""
    print("\n🧪 Testing Flask App Logging")
    print("=" * 40)
    
    try:
        from flask import Flask
        from utils.logging_config import setup_logging
        
        # Create temporary Flask app
        app = Flask(__name__)
        app.config.update({
            'LOG_LEVEL': 'INFO',
            'LOG_DIR': './test_logs',
            'LOG_FILE': './test_logs/test_app.log'
        })
        
        # Setup logging
        setup_logging(app)
        
        # Test app logging
        app.logger.info("Test Flask app log message")
        app.logger.warning("Test Flask app warning")
        app.logger.error("Test Flask app error")
        
        print("✅ Flask app logging setup successful")
        
        # Clean up
        if os.path.exists('./test_logs'):
            shutil.rmtree('./test_logs')
        
        return True
        
    except Exception as e:
        print(f"❌ Flask logging test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Backend Logging Component Test")
    print("=" * 50)
    
    # Test logging configuration
    logging_ok = test_logging_config()
    
    # Test Flask logging
    flask_logging_ok = test_flask_logging()
    
    print("\n" + "=" * 50)
    print("📊 LOGGING TEST RESULTS:")
    print(f"✅ Logging Configuration: {'PASS' if logging_ok else 'FAIL'}")
    print(f"✅ Flask Logging Setup: {'PASS' if flask_logging_ok else 'FAIL'}")
    
    if logging_ok and flask_logging_ok:
        print("\n🎉 ALL LOGGING TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME LOGGING TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


