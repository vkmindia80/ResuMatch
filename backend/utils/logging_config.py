import logging
import sys
from datetime import datetime
import json
from typing import Any, Dict
import traceback

# Custom JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """Setup application logging with JSON formatting"""
    
    # Create logger
    logger = logging.getLogger("resumatch")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler for errors
    try:
        error_handler = logging.FileHandler("/var/log/supervisor/backend.err.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        logger.addHandler(error_handler)
    except:
        # If can't write to file, just use console
        pass
    
    # File handler for all logs
    try:
        file_handler = logging.FileHandler("/var/log/supervisor/backend.out.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    except:
        # If can't write to file, just use console
        pass
    
    return logger


# Create global logger instance
app_logger = setup_logging()


def log_api_request(request_id: str, method: str, endpoint: str, user_id: str = None):
    """Log API request"""
    extra = {
        "request_id": request_id,
        "method": method,
        "endpoint": endpoint,
    }
    if user_id:
        extra["user_id"] = user_id
    
    app_logger.info(f"API Request: {method} {endpoint}", extra=extra)


def log_api_response(request_id: str, status_code: int, duration_ms: float):
    """Log API response"""
    app_logger.info(
        f"API Response: {status_code}",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
    )


def log_error(message: str, exc_info=None, **kwargs):
    """Log error with optional exception info"""
    app_logger.error(message, exc_info=exc_info, extra=kwargs)


def log_warning(message: str, **kwargs):
    """Log warning"""
    app_logger.warning(message, extra=kwargs)


def log_info(message: str, **kwargs):
    """Log info"""
    app_logger.info(message, extra=kwargs)
