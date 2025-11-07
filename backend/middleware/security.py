from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import uuid
from utils.logging_config import log_api_request, log_api_response, log_error

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}

# Max request body size (10MB)
MAX_BODY_SIZE = 10 * 1024 * 1024


async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response


async def request_logging_middleware(request: Request, call_next):
    """Log all API requests and responses with timing"""
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    user_id = getattr(request.state, "user_id", None)
    log_api_request(
        request_id=request_id,
        method=request.method,
        endpoint=str(request.url.path),
        user_id=user_id
    )
    
    # Start timer
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        log_api_response(
            request_id=request_id,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    except Exception as e:
        # Log error
        duration_ms = (time.time() - start_time) * 1000
        log_error(
            f"Request failed: {str(e)}",
            exc_info=True,
            request_id=request_id,
            endpoint=str(request.url.path),
            method=request.method,
            duration_ms=round(duration_ms, 2)
        )
        
        # Re-raise exception
        raise


async def validate_content_length(request: Request, call_next):
    """Validate request body size to prevent DoS attacks"""
    content_length = request.headers.get("content-length")
    
    if content_length:
        try:
            content_length = int(content_length)
            if content_length > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "detail": f"Request body too large. Maximum size is {MAX_BODY_SIZE / (1024*1024)}MB"
                    }
                )
        except ValueError:
            pass
    
    response = await call_next(request)
    return response
