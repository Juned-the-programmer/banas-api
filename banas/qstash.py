"""
Simplified QStash client for scheduled task management.
No webhook receiver needed - tasks are called via HTTP endpoints.
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Only import QStash if token is configured
if hasattr(settings, 'QSTASH_TOKEN') and settings.QSTASH_TOKEN:
    try:
        from qstash import QStash
        qstash_client = QStash(token=settings.QSTASH_TOKEN)
    except ImportError:
        logger.warning("QStash SDK not installed. Scheduled tasks will not work.")
        qstash_client = None
else:
    logger.info("QSTASH_TOKEN not configured. Scheduled tasks disabled.")
    qstash_client = None
