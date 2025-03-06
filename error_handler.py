import logging
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('error_logs.txt')
    ]
)

logger = logging.getLogger('error_handler')

class ResearchError(Exception):
    """Base exception class for research-related errors"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class APIError(ResearchError):
    """Exception for API-related errors"""
    def __init__(self, message: str, status_code: int, response_body: Any = None):
        super().__init__(
            message=message,
            error_code=f"API_{status_code}",
            details={
                "status_code": status_code,
                "response_body": response_body
            }
        )

class ValidationError(ResearchError):
    """Exception for input validation errors"""
    def __init__(self, message: str, invalid_fields: Dict[str, str]):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"invalid_fields": invalid_fields}
        )

class TavilyAPIError(APIError):
    """Specific exception for Tavily API errors"""
    def __init__(self, message: str, status_code: int, response_body: Any = None):
        super().__init__(
            message=f"Tavily API Error: {message}",
            status_code=status_code,
            response_body=response_body
        )
        self.details["api_name"] = "Tavily"

def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format an error into a standardized response structure"""
    try:
        if isinstance(error, ResearchError):
            response = {
                "status": "error",
                "message": str(error.message),
                "error_code": error.error_code,
                "details": error.details,
                "timestamp": error.timestamp
            }
        else:
            response = {
                "status": "error",
                "message": str(error),
                "error_code": "UNKNOWN_ERROR",
                "details": {
                    "type": error.__class__.__name__,
                    "traceback": traceback.format_exc()
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Ensure response is JSON serializable
        try:
            json.dumps(response)
        except (TypeError, ValueError) as e:
            logger.error(f"Response not JSON serializable: {str(e)}")
            # Create a safe response
            response = {
                "status": "error",
                "message": "Internal server error - Response not serializable",
                "error_code": "SERIALIZATION_ERROR",
                "details": {
                    "original_error": str(error),
                    "serialization_error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Log the error
        logger.error(
            f"Error occurred: {response['error_code']} - {response['message']}\n"
            f"Details: {json.dumps(response['details'], indent=2)}"
        )
        
        return response
        
    except Exception as e:
        # Fallback response if everything else fails
        logger.error(f"Critical error in error handling: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Critical error in error handling",
            "error_code": "CRITICAL_ERROR",
            "timestamp": datetime.now().isoformat()
        }

def validate_tavily_request(query: str, depth: int) -> None:
    """Validate Tavily API request parameters"""
    errors = {}
    
    if not query or not isinstance(query, str):
        errors["query"] = "Query must be a non-empty string"
    elif len(query.strip()) < 3:
        errors["query"] = "Query must be at least 3 characters long"
    
    if not isinstance(depth, int):
        errors["depth"] = "Depth must be an integer"
    elif depth < 1 or depth > 5:
        errors["depth"] = "Depth must be between 1 and 5"
    
    if errors:
        raise ValidationError(
            message="Invalid request parameters",
            invalid_fields=errors
        )

def handle_tavily_error(status_code: int, response_body: Any) -> None:
    """Handle Tavily API specific errors"""
    error_messages = {
        400: "Bad request - Please check your query parameters",
        401: "Unauthorized - Invalid API key",
        403: "Forbidden - Please check your API permissions",
        422: "Unprocessable Entity - Invalid request format",
        429: "Too Many Requests - Rate limit exceeded",
        500: "Internal Server Error - Tavily API is experiencing issues",
        503: "Service Unavailable - Tavily API is temporarily unavailable"
    }
    
    message = error_messages.get(status_code, f"Unknown error occurred (Status: {status_code})")
    raise TavilyAPIError(message, status_code, response_body)

def error_handler(func):
    """Decorator to handle errors in async functions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            
            # Validate result is JSON serializable
            try:
                json.dumps(result)
                return result
            except (TypeError, ValueError) as e:
                logger.error(f"Function result not JSON serializable: {str(e)}")
                return format_error_response(ValueError(f"Response not JSON serializable: {str(e)}"))
                
        except ResearchError as e:
            # Already formatted, just return
            return format_error_response(e)
        except Exception as e:
            # Log unexpected errors with full traceback
            logger.error(
                f"Unexpected error in {func.__name__}:",
                exc_info=True,
                extra={
                    "args": args,
                    "kwargs": kwargs,
                    "function": func.__name__
                }
            )
            return format_error_response(e)
    return wrapper

def log_api_call(api_name: str, params: Dict[str, Any]) -> None:
    """Log API call details"""
    logger.info(
        f"API Call to {api_name}:\n"
        f"Parameters: {json.dumps(params, indent=2)}"
    )

def log_api_response(api_name: str, response: Any) -> None:
    """Log API response details"""
    try:
        response_data = response if isinstance(response, dict) else {"raw_response": str(response)}
        logger.info(
            f"Response from {api_name}:\n"
            f"Response: {json.dumps(response_data, indent=2)}"
        )
    except Exception as e:
        logger.warning(f"Could not log {api_name} response: {str(e)}")

class ErrorTracker:
    """Track and analyze errors over time"""
    def __init__(self):
        self.error_log_file = "error_statistics.json"
        self.error_stats = self._load_error_stats()
    
    def _load_error_stats(self) -> Dict[str, Any]:
        """Load existing error statistics"""
        if os.path.exists(self.error_log_file):
            try:
                with open(self.error_log_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self._initialize_error_stats()
        return self._initialize_error_stats()
    
    def _initialize_error_stats(self) -> Dict[str, Any]:
        """Initialize error statistics structure"""
        return {
            "total_errors": 0,
            "error_types": {},
            "error_timeline": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def track_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Track an error occurrence"""
        error_type = error.__class__.__name__
        timestamp = datetime.now().isoformat()
        
        # Update statistics
        self.error_stats["total_errors"] += 1
        self.error_stats["error_types"][error_type] = self.error_stats["error_types"].get(error_type, 0) + 1
        
        # Add to timeline
        self.error_stats["error_timeline"].append({
            "timestamp": timestamp,
            "error_type": error_type,
            "message": str(error),
            "context": context or {}
        })
        
        # Keep only last 100 errors in timeline
        if len(self.error_stats["error_timeline"]) > 100:
            self.error_stats["error_timeline"] = self.error_stats["error_timeline"][-100:]
        
        self.error_stats["last_updated"] = timestamp
        
        # Save updated stats
        try:
            with open(self.error_log_file, 'w') as f:
                json.dump(self.error_stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save error statistics: {str(e)}")

# Initialize error tracker
error_tracker = ErrorTracker() 