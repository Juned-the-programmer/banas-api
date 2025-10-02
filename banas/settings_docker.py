"""
Django settings for Docker container testing.
Uses minimal dependencies for testing Docker builds and health checks.
"""

import pathlib

# Override for Docker testing
DEBUG = False
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1", "0.0.0.0"]  # nosec

# Use SQLite for Docker testing (faster than setting up PostgreSQL in CI)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/docker_test.db",  # nosec
    }
}

# Simplified static files for Docker testing
STATIC_ROOT = "/app/static"
MEDIA_ROOT = "/app/media"

# Ensure directories exist
pathlib.Path(STATIC_ROOT).mkdir(parents=True, exist_ok=True)
pathlib.Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

# Docker-specific logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Health check settings
HEALTH_CHECK_URL = "/health/"
