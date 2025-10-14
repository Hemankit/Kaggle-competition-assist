#!/usr/bin/env python3
"""
Test Flask app creation and configuration
"""

import sys
import os
import tempfile
import shutil

# Add the backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kaggle_competition_assist_backend'))

def test_flask_app_creation():
    """Test Flask app creation"""
    print("🧪 Testing Flask App Creation")
    print("=" * 40)
    
    try:
        from app import create_app
        
        # Create Flask app
        app = create_app()
        
        print("✅ Flask app creation successful")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Config loaded: {len(app.config)} config values")
        
        return app
        
    except Exception as e:
        print(f"❌ Flask app creation failed: {str(e)}")
        return None

def test_flask_app_configuration(app):
    """Test Flask app configuration"""
    print("\n🧪 Testing Flask App Configuration")
    print("=" * 40)
    
    try:
        # Test configuration values
        config_keys = [
            'LOG_LEVEL', 'LOG_DIR', 'LOG_FILE',
            'GOOGLE_API_KEY', 'DEEPSEEK_API_KEY',
            'HUGGINGFACEHUB_API_TOKEN', 'GROQ_API_KEY',
            'DATA_DIR', 'FAISS_INDEX_PATH', 'REDIS_URL'
        ]
        
        for key in config_keys:
            value = app.config.get(key, 'NOT_SET')
            if value == 'NOT_SET':
                print(f"⚠️  Config {key}: NOT_SET")
            else:
                print(f"✅ Config {key}: {'SET' if value else 'EMPTY'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app configuration test failed: {str(e)}")
        return False

def test_flask_blueprints(app):
    """Test Flask blueprints registration"""
    print("\n🧪 Testing Flask Blueprints")
    print("=" * 40)
    
    try:
        # Get registered blueprints
        blueprints = list(app.blueprints.keys())
        
        expected_blueprints = [
            'health', 'input_processsing', 'scraping_or_fetching',
            'RAG_pipe', 'multiAgent', 'eval', 'graph_visualization', 'query'
        ]
        
        print(f"✅ Registered blueprints: {blueprints}")
        
        for blueprint in expected_blueprints:
            if blueprint in blueprints:
                print(f"✅ Blueprint '{blueprint}': REGISTERED")
            else:
                print(f"⚠️  Blueprint '{blueprint}': MISSING")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask blueprints test failed: {str(e)}")
        return False

def test_flask_logging_setup(app):
    """Test Flask logging setup"""
    print("\n🧪 Testing Flask Logging Setup")
    print("=" * 40)
    
    try:
        # Test logging
        app.logger.info("Test log message from Flask app")
        app.logger.warning("Test warning message")
        app.logger.error("Test error message")
        
        print("✅ Flask app logging working")
        
        # Check if log file exists
        log_file = app.config.get('LOG_FILE', './logs/kaggle_assist.log')
        if os.path.exists(log_file):
            print(f"✅ Log file exists: {log_file}")
        else:
            print(f"⚠️  Log file not found: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask logging setup test failed: {str(e)}")
        return False

def test_health_check_with_app_context(app):
    """Test health check functions with Flask app context"""
    print("\n🧪 Testing Health Check with App Context")
    print("=" * 40)
    
    try:
        with app.app_context():
            from utils.health_check import (
                check_database_connection,
                check_llm_services,
                check_file_system,
                get_system_metrics,
                comprehensive_health_check
            )
            
            # Test database connection
            db_status = check_database_connection()
            print(f"✅ Database status: {db_status['status']}")
            
            # Test LLM services
            llm_status = check_llm_services()
            configured_services = [k for k, v in llm_status.items() if v['status'] == 'configured']
            print(f"✅ LLM services configured: {configured_services}")
            
            # Test file system
            fs_status = check_file_system()
            print(f"✅ File system checks: {len(fs_status)} checks performed")
            
            # Test system metrics
            metrics = get_system_metrics()
            if 'error' not in metrics:
                print(f"✅ System metrics: CPU {metrics['cpu_percent']}%, Memory {metrics['memory']['percent']}%")
            else:
                print(f"⚠️  System metrics error: {metrics['error']}")
            
            # Test comprehensive health check
            health_report = comprehensive_health_check()
            print(f"✅ Overall health status: {health_report['overall_status']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Health check with app context test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Backend Flask App Component Test")
    print("=" * 50)
    
    # Test Flask app creation
    app = test_flask_app_creation()
    if not app:
        print("\n❌ CANNOT CONTINUE - Flask app creation failed!")
        return False
    
    # Test configuration
    config_ok = test_flask_app_configuration(app)
    
    # Test blueprints
    blueprints_ok = test_flask_blueprints(app)
    
    # Test logging
    logging_ok = test_flask_logging_setup(app)
    
    # Test health checks with app context
    health_ok = test_health_check_with_app_context(app)
    
    print("\n" + "=" * 50)
    print("📊 FLASK APP TEST RESULTS:")
    print(f"✅ Flask App Creation: PASS")
    print(f"✅ Configuration: {'PASS' if config_ok else 'FAIL'}")
    print(f"✅ Blueprints: {'PASS' if blueprints_ok else 'FAIL'}")
    print(f"✅ Logging Setup: {'PASS' if logging_ok else 'FAIL'}")
    print(f"✅ Health Checks: {'PASS' if health_ok else 'FAIL'}")
    
    if config_ok and blueprints_ok and logging_ok and health_ok:
        print("\n🎉 ALL FLASK APP TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME FLASK APP TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


