"""
Health check API endpoints for Kaggle Competition Assistant Backend
"""

from flask import Blueprint, jsonify
try:
    from ..utils.health_check import comprehensive_health_check, check_database_connection, check_llm_services
    from ..utils.logging_config import get_request_logger, log_request
except ImportError:
    # Fallback for when running from project root
    from utils.health_check import comprehensive_health_check, check_database_connection, check_llm_services
    from utils.logging_config import get_request_logger, log_request

health_bp = Blueprint("health", __name__, url_prefix="/health")


@health_bp.route("/", methods=["GET"])
@log_request
def health_check():
    """
    Comprehensive health check endpoint
    """
    logger = get_request_logger()
    logger.info("Health check requested")
    
    try:
        health_report = comprehensive_health_check()
        
        # Return appropriate HTTP status code based on health
        status_code = 200
        if health_report["overall_status"] == "unhealthy":
            status_code = 503
        elif health_report["overall_status"] == "degraded":
            status_code = 206
        
        logger.info(f"Health check completed with status: {health_report['overall_status']}")
        return jsonify(health_report), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "timestamp": "2024-01-01T00:00:00",
            "overall_status": "unhealthy",
            "error": str(e),
            "checks": {}
        }), 503


@health_bp.route("/simple", methods=["GET"])
@log_request
def simple_health_check():
    """
    Simple health check endpoint (just returns OK if the app is running)
    """
    return jsonify({
        "status": "healthy",
        "message": "Kaggle Competition Assistant Backend is running",
        "timestamp": "2024-01-01T00:00:00"
    }), 200


@health_bp.route("/database", methods=["GET"])
@log_request
def database_health():
    """
    Database connectivity health check
    """
    try:
        db_status = check_database_connection()
        status_code = 200 if db_status["status"] == "healthy" else 503
        return jsonify(db_status), status_code
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": f"Database check failed: {str(e)}"
        }), 503


@health_bp.route("/llm", methods=["GET"])
@log_request
def llm_health():
    """
    LLM services health check
    """
    try:
        llm_status = check_llm_services()
        return jsonify(llm_status), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": f"LLM check failed: {str(e)}"
        }), 503


@health_bp.route("/ready", methods=["GET"])
@log_request
def readiness_check():
    """
    Readiness check for Kubernetes/Docker deployments
    """
    try:
        # Check if essential services are ready
        db_status = check_database_connection()
        llm_status = check_llm_services()
        
        # Consider the app ready if database is healthy and at least one LLM is configured
        is_ready = (
            db_status["status"] in ["healthy", "not_configured"] and
            any(service["status"] == "configured" for service in llm_status.values())
        )
        
        if is_ready:
            return jsonify({
                "status": "ready",
                "message": "Application is ready to serve requests"
            }), 200
        else:
            return jsonify({
                "status": "not_ready",
                "message": "Application is not ready to serve requests"
            }), 503
            
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "message": f"Readiness check failed: {str(e)}"
        }), 503


@health_bp.route("/live", methods=["GET"])
@log_request
def liveness_check():
    """
    Liveness check for Kubernetes/Docker deployments
    """
    return jsonify({
        "status": "alive",
        "message": "Application is alive and responding"
    }), 200
