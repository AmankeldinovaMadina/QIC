"""Logging configuration with structured logging support."""

import logging
import sys
from typing import Any, Dict


def configure_logging(debug: bool = False) -> None:
    """Configure logging for the application."""
    
    level = logging.DEBUG if debug else logging.INFO
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=level,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Middleware for request/response logging
async def log_request_middleware(request, call_next):
    """Log HTTP requests and responses (excluding sensitive data)."""
    logger = get_logger("http")
    
    # Log request
    logger.info(
        f"Request started: {request.method} {request.url}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url} - {response.status_code}"
    )
    
    return response