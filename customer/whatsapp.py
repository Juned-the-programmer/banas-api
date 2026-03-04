import json
import logging

from django.conf import settings

from banas.qstash import qstash_client

logger = logging.getLogger(__name__)


def format_phone_number(phone: str) -> str:
    """
    Strips + or 0 from the beginning and ensures the standard country code format.
    Assumes India (+91) if no country code or 10 digits are provided.
    """
    if not phone:
        return ""

    cleaned = "".join(filter(str.isdigit, phone))

    # If standard 10 digit Indian number, prefix with 91
    if len(cleaned) == 10:
        return f"91{cleaned}"

    # If the user included 0 at the start of a 10 digit number
    if len(cleaned) == 11 and cleaned.startswith("0"):
        return f"91{cleaned[1:]}"

    return cleaned


def enqueue_whatsapp_message(phone: str, message: str) -> None:
    """
    Pushes a formatting WhatsApp message into the pacing QStash queue.
    The worker will execute it with a 3-second delay to prevent rate limits.
    """
    formatted_phone = format_phone_number(phone)
    if not formatted_phone:
        logger.warning(f"Skipping WhatsApp enqueue: Invalid phone number '{phone}'")
        return

    if not settings.BASE_URL:
        logger.warning("Skipping WhatsApp enqueue: BASE_URL is not set")
        return

    payload = {"phone": formatted_phone, "message": message}

    webhook_url = f"{settings.BASE_URL.rstrip('/')}/api/customer/tasks/send-whatsapp/"

    try:
        # We don't use the async_helpers decorator here because we explicitly
        # want to send it to the named pace-controlled queue.
        if qstash_client:
            try:
                res = qstash_client.message.enqueue_json(
                    url=webhook_url,
                    body=payload,
                    queue="whatsapp-messages",
                )
                logger.info(f"Enqueued WhatsApp message to {formatted_phone}: {res.message_id}")
            except Exception as e:
                logger.error(f"Failed to enqueue WhatsApp message to QStash for {formatted_phone}: {str(e)}", exc_info=True)
        else:
            logger.info(f"[LOCAL DEV] Enqueue WhatsApp message to {formatted_phone}: {message[:30]}...")

    except Exception as e:
        logger.error(f"Failed to prep WhatsApp message for {formatted_phone}: {str(e)}", exc_info=True)
