from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import os

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Global default: 100 requests per minute
    storage_uri=os.getenv("REDIS_URL", "memory://")  # Use memory storage (or Redis if available)
)

# Custom rate limit configurations
RATE_LIMITS = {
    "auth": "20/minute",      # Auth endpoints: 20 requests per minute
    "heavy": "10/minute",     # Heavy operations (AI generation): 10 per minute
    "standard": "100/minute", # Standard endpoints: 100 per minute
}


def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from request for user-specific rate limiting"""
    try:
        # Try to get user_id from request state (set by auth middleware)
        if hasattr(request.state, "user_id"):
            return request.state.user_id
    except:
        pass
    
    # Fallback to IP address
    return get_remote_address(request)
