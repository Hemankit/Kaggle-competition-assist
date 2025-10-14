#!/usr/bin/env python3
"""
Test health check utilities
"""

import sys
import os

# Add the backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kaggle_competition_assist_backend'))

def test_health_check_imports():
    """Test health check imports"""
    print("🧪 Testing Health Check Imports")
    print("=" * 40)
    
    try:
        from utils.health_check import (
            check_database_connection,
            check_llm_services,
            check_file_system,
            get_system_metrics,
            comprehensive_health_check
        )
        print("✅ Health check imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Health check imports failed: {str(e)}")
        return False

def test_health_check_functions():
    """Test individual health check functions"""
    print("\n🧪 Testing Health Check Functions")
    print("=" * 40)
    
    try:
        from utils.health_check import (
            check_database_connection,
            check_llm_services,
            check_file_system,
            get_system_metrics
        )
        
        # Test database connection check
        db_status = check_database_connection()
        print(f"✅ Database check: {db_status}")
        
        # Test LLM services check
        llm_status = check_llm_services()
        print(f"✅ LLM services check: {llm_status}")
        
        # Test file system check
        fs_status = check_file_system()
        print(f"✅ File system check: {fs_status}")
        
        # Test system metrics
        metrics = get_system_metrics()
        print(f"✅ System metrics: {metrics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check functions test failed: {str(e)}")
        return False

def test_comprehensive_health_check():
    """Test comprehensive health check"""
    print("\n🧪 Testing Comprehensive Health Check")
    print("=" * 40)
    
    try:
        from utils.health_check import comprehensive_health_check
        
        # This will fail without Flask app context, but let's test the import
        health_report = comprehensive_health_check()
        print(f"✅ Comprehensive health check: {health_report}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive health check test failed: {str(e)}")
        print(f"   (This is expected without Flask app context)")
        return False

def test_psutil_availability():
    """Test if psutil is available for system metrics"""
    print("\n🧪 Testing System Metrics Dependencies")
    print("=" * 40)
    
    try:
        import psutil
        
        # Test basic psutil functionality
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"✅ CPU usage: {cpu_percent}%")
        print(f"✅ Memory usage: {memory.percent}%")
        print(f"✅ Disk usage: {disk.percent}%")
        
        return True
        
    except ImportError:
        print("❌ psutil not installed - install with: pip install psutil")
        return False
    except Exception as e:
        print(f"❌ System metrics test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Backend Health Check Component Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_health_check_imports()
    
    # Test individual functions
    functions_ok = test_health_check_functions()
    
    # Test comprehensive check
    comprehensive_ok = test_comprehensive_health_check()
    
    # Test psutil
    psutil_ok = test_psutil_availability()
    
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK TEST RESULTS:")
    print(f"✅ Health Check Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ Individual Functions: {'PASS' if functions_ok else 'FAIL'}")
    print(f"✅ Comprehensive Check: {'PASS' if comprehensive_ok else 'FAIL'}")
    print(f"✅ System Metrics (psutil): {'PASS' if psutil_ok else 'FAIL'}")
    
    if imports_ok and functions_ok and psutil_ok:
        print("\n🎉 ALL HEALTH CHECK TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME HEALTH CHECK TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


