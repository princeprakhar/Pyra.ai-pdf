from fastapi import Request
import logging

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    try:
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
