"""
Async task helpers.

In production (BASE_URL + QSTASH_TOKEN set): publishes task to a QStash named
queue (if queue_name given) or as a plain message. Falls back to threading locally.

In local development (no BASE_URL): falls back to Python threading.
"""

from functools import wraps
import logging
import threading

logger = logging.getLogger(__name__)


def async_task(endpoint_path, queue=None):
    """
    Decorator that publishes a task to a QStash named queue (production) or runs
    it in a background thread (local dev).

    Args:
        endpoint_path: The URL path for the QStash callback endpoint,
                       e.g. "/api/tasks/send-email/"
        queue:         Optional QStash queue name, e.g. "send-email".
                       When set, task appears in QStash Queues tab with
                       ordering and concurrency control.

    Usage:
        @async_task("/api/tasks/send-email/", queue="send-email")
        def send_async_email(subject, message, sender, recipient_list, html_message):
            ...

        # Call it normally - returns immediately
        send_async_email("Hello", "World", ...)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Import here to avoid circular imports at module load time
            from django.conf import settings

            from banas.qstash import qstash_client

            base_url = getattr(settings, "BASE_URL", "").rstrip("/")

            if qstash_client and base_url:
                # --- Production: publish to QStash ---
                full_url = f"{base_url}{endpoint_path}"
                # Serialize args/kwargs; UUIDs must be str
                payload = {
                    "args": [str(a) if hasattr(a, "hex") else a for a in args],
                    "kwargs": {k: str(v) if hasattr(v, "hex") else v for k, v in kwargs.items()},
                }
                try:
                    if queue:
                        # Named queue: visible in QStash Queues tab, ordered, concurrency-controlled
                        qstash_client.message.enqueue_json(
                            queue=queue,
                            url=full_url,
                            body=payload,
                            retries=3,
                        )
                        logger.info(f"Enqueued async task '{func.__name__}' → queue='{queue}' url={full_url}")
                    else:
                        # Plain message: fire-and-forget
                        qstash_client.message.publish_json(
                            url=full_url,
                            body=payload,
                            retries=3,
                        )
                        logger.info(f"Published async task '{func.__name__}' → {full_url}")
                except Exception as e:
                    logger.error(f"QStash publish failed for '{func.__name__}': {e}. Falling back to thread.", exc_info=True)
                    _run_in_thread(func, args, kwargs)
            else:
                # --- Local dev: run in background thread ---
                logger.debug(f"No QStash/BASE_URL configured. Running '{func.__name__}' in thread.")
                _run_in_thread(func, args, kwargs)

        return wrapper

    return decorator


def _run_in_thread(func, args, kwargs):
    """Helper to run a function in a daemon thread."""

    def run_task():
        try:
            logger.info(f"Starting async task in thread: {func.__name__}")
            func(*args, **kwargs)
            logger.info(f"Completed async task: {func.__name__}")
        except Exception as e:
            logger.error(f"Error in async task {func.__name__}: {e}", exc_info=True)

    thread = threading.Thread(target=run_task, daemon=True)
    thread.start()
