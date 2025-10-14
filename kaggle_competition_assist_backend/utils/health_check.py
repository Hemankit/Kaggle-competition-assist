"""
Health check utilities for Kaggle Competition Assistant Backend
"""

import time
import psutil
import os
from datetime import datetime
from flask import current_app


def check_database_connection():
    """
    Check if database connections are working
    """
    try:
        # Add your database connection checks here
        # For now, we'll check if Redis is available (if configured)
        redis_url = current_app.config.get('REDIS_URL')
        if redis_url and 'redis://' in redis_url:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            return {"status": "healthy", "message": "Redis connection successful"}
        else:
            return {"status": "not_configured", "message": "Redis not configured"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}


def check_llm_services():
    """
    Check if LLM services are accessible
    """
    health_status = {}
    
    # Check environment variables for API keys
    api_keys = {
        "google": current_app.config.get('GOOGLE_API_KEY'),
        "deepseek": current_app.config.get('DEEPSEEK_API_KEY'),
        "huggingface": current_app.config.get('HUGGINGFACEHUB_API_TOKEN'),
        "groq": current_app.config.get('GROQ_API_KEY')
    }
    
    for service, api_key in api_keys.items():
        if api_key:
            health_status[service] = {"status": "configured", "message": "API key present"}
        else:
            health_status[service] = {"status": "not_configured", "message": "API key missing"}
    
    return health_status


def check_file_system():
    """
    Check if required directories and files exist
    """
    checks = {}
    
    # Check log directory
    log_dir = current_app.config.get('LOG_DIR', './logs')
    if os.path.exists(log_dir):
        checks["log_directory"] = {"status": "healthy", "message": f"Log directory exists: {log_dir}"}
    else:
        checks["log_directory"] = {"status": "unhealthy", "message": f"Log directory missing: {log_dir}"}
    
    # Check data directory
    data_dir = current_app.config.get('DATA_DIR', './data')
    if os.path.exists(data_dir):
        checks["data_directory"] = {"status": "healthy", "message": f"Data directory exists: {data_dir}"}
    else:
        checks["data_directory"] = {"status": "warning", "message": f"Data directory missing: {data_dir}"}
    
    # Check FAISS index
    faiss_path = current_app.config.get('FAISS_INDEX_PATH', './vector_store/faiss_index')
    if os.path.exists(faiss_path):
        checks["faiss_index"] = {"status": "healthy", "message": f"FAISS index exists: {faiss_path}"}
    else:
        checks["faiss_index"] = {"status": "warning", "message": f"FAISS index missing: {faiss_path}"}
    
    return checks


def get_system_metrics():
    """
    Get system resource metrics
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
    except Exception as e:
        return {"error": f"Failed to get system metrics: {str(e)}"}


def comprehensive_health_check():
    """
    Perform a comprehensive health check of the system
    """
    start_time = time.time()
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "checks": {
            "database": check_database_connection(),
            "llm_services": check_llm_services(),
            "file_system": check_file_system(),
            "system_metrics": get_system_metrics()
        },
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    # Determine overall status
    all_checks = []
    for category, checks in health_report["checks"].items():
        if isinstance(checks, dict):
            if "status" in checks:
                all_checks.append(checks["status"])
            else:
                for check_name, check_result in checks.items():
                    if isinstance(check_result, dict) and "status" in check_result:
                        all_checks.append(check_result["status"])
    
    # Set overall status based on individual checks
    if any(status == "unhealthy" for status in all_checks):
        health_report["overall_status"] = "unhealthy"
    elif any(status == "warning" for status in all_checks):
        health_report["overall_status"] = "degraded"
    elif any(status == "not_configured" for status in all_checks):
        health_report["overall_status"] = "partial"
    
    return health_report


