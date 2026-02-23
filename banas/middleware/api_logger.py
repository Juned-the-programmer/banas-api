import json
import logging
import time

logger = logging.getLogger("banas.api")

class APILoggerMiddleware:
    """
    Middleware to log all incoming API requests and their responses.
    Logs method, path, query params, body size, and response time.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_keys = {"password", "token", "access", "refresh", "authorization"}

    def __call__(self, request):
        # Only log API interactions
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        start_time = time.time()

        # Try to parse body for logging (only if it's JSON)
        request_body = None
        if request.content_type == "application/json" and request.body:
            try:
                body_json = json.loads(request.body)
                request_body = self._mask_sensitive_data(body_json)
            except json.JSONDecodeError:
                request_body = "<invalid json>"

        # --- Process the Request ---
        response = self.get_response(request)
        # ---------------------------

        duration_ms = int((time.time() - start_time) * 1000)
        
        # Build the log message
        user = request.user.username if hasattr(request, "user") and request.user.is_authenticated else "Anonymous"
        ip_addr = self._get_client_ip(request)
        
        log_data = {
            "method": request.method,
            "path": request.path,
            "query": dict(request.GET) if request.GET else None,
            "user": user,
            "ip": ip_addr,
            "status": response.status_code,
            "time_ms": duration_ms,
        }

        if request_body:
            log_data["body"] = request_body

        # Log at appropriate level
        log_message = f"[{request.method}] {request.path} | HTTP {response.status_code} | {duration_ms}ms | User: {user} | IP: {ip_addr}"

        if response.status_code >= 500:
            logger.error(f"SERVER ERROR: {log_message} | Data: {log_data}")
        elif response.status_code >= 400:
            logger.warning(f"CLIENT ERROR: {log_message} | Data: {log_data}")
        else:
            logger.info(f"SUCCESS: {log_message}")

        return response

    def _mask_sensitive_data(self, data):
        """Recursively mask sensitive keys in a dictionary."""
        if isinstance(data, dict):
            masked = {}
            for k, v in data.items():
                if any(sensitive in k.lower() for sensitive in self.sensitive_keys):
                    masked[k] = "***MASKED***"
                else:
                    masked[k] = self._mask_sensitive_data(v)
            return masked
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        return data

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
