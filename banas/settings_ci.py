"""
Django settings for CI/Testing environment.
Uses SQLite and removes external dependencies for GitHub Actions.
"""

from .settings import *
import os

# Override DEBUG for CI
DEBUG = False
ALLOWED_HOSTS = ['*']

# Use SQLite for CI testing instead of PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for speed
    }
}

# Disable Redis cache for CI - use dummy cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery for CI
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable external storage for CI
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files for CI
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Remove external dependencies that aren't needed for CI
# Remove AWS and Redis related configurations
AWS_ACCESS_KEY_ID = 'test'
AWS_SECRET_ACCESS_KEY = 'test'
AWS_STORAGE_BUCKET_NAME = 'test'
AWS_S3_REGION_NAME = 'us-east-1'

# Disable logging for CI
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# Disable API logger middleware for CI
MIDDLEWARE = [m for m in MIDDLEWARE if 'drf_api_logger' not in m]

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Set a test secret key
SECRET_KEY = 'test-secret-key-for-ci-only-not-for-production'