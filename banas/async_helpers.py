"""
Simple async task helpers using Python threading.
For I/O-bound tasks like sending emails, generating QR codes, etc.
"""
import logging
import threading
from functools import wraps

logger = logging.getLogger(__name__)


def async_task(func):
    """
    Decorator to run a function asynchronously in a background thread.
    
    Usage:
        @async_task
        def send_email(subject, message):
            # Email sending logic
            pass
        
        # Call it normally - returns immediately
        send_email("Hello", "World")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        def run_task():
            try:
                logger.info(f"Starting async task: {func.__name__}")
                func(*args, **kwargs)
                logger.info(f"Completed async task: {func.__name__}")
            except Exception as e:
                logger.error(f"Error in async task {func.__name__}: {e}", exc_info=True)
        
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        logger.debug(f"Started background thread for: {func.__name__}")
    
    return wrapper
