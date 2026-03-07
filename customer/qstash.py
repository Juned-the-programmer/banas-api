import logging
import time

from django.conf import settings
import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .task import generate_customer_qr_code_for_daily_entry_async, send_async_email

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def task_send_email(request):
    """
    QStash callback: Send email.
    Payload: { args: [subject, message, sender, recipient_list, html_message] }
    """
    try:
        data = request.data
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})

        subject = args[0] if len(args) > 0 else kwargs.get("subject")
        message = args[1] if len(args) > 1 else kwargs.get("message")
        sender = args[2] if len(args) > 2 else kwargs.get("sender")
        recipient_list = args[3] if len(args) > 3 else kwargs.get("recipient_list")
        html_message = args[4] if len(args) > 4 else kwargs.get("html_message")

        if not all([subject, message, sender, recipient_list, html_message]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        send_async_email.__wrapped__(subject, message, sender, recipient_list, html_message)
        logger.info(f"Email task completed for: {recipient_list}")
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Email task failed: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def task_generate_qr(request):
    """
    QStash callback: Generate QR code for a customer.
    Payload: { args: [customer_id] }
    """

    try:
        data = request.data
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})

        customer_id = args[0] if args else kwargs.get("customer_id")
        if not customer_id:
            return Response({"error": "Missing customer_id"}, status=status.HTTP_400_BAD_REQUEST)

        generate_customer_qr_code_for_daily_entry_async.__wrapped__(customer_id)
        logger.info(f"QR code task completed for customer: {customer_id}")
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"QR code task failed: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def task_send_whatsapp(request):
    """
    QStash callback: Sends a WhatsApp message via Evolution API.
    Payload: {"phone": "91...", "message": "..."}
    """
    try:
        data = request.data
        phone = data.get("phone")
        message = data.get("message")

        if not phone or not message:
            return Response({"error": "Missing phone or message"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Prepare Evolution API Payload
        url = f"{settings.EVOLUTION_BASE_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
        headers = {"apikey": settings.EVOLUTION_API_KEY, "Content-Type": "application/json"}
        payload = {"number": phone, "text": message}

        # 2. Fire Request
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        # We don't fail the task if the user's number is invalid (400), but we log it.
        # If the Evolution API goes down (500), we raise an exception so QStash retries later.
        if response.status_code >= 500:
            response.raise_for_status()

        logger.info(f"WhatsApp sent to {phone} | Evolution Status: {response.status_code}")

        # 3. PACING DELAY (Crucial for anti-ban)
        # We block this worker for 3 seconds before returning 200 OK.
        # Since queue parallelism=1, QStash will physically wait 3 seconds before sending the next one.
        time.sleep(3)

        return Response({"status": "ok", "evolution_status": response.status_code}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"WhatsApp task failed: {str(e)}", exc_info=True)
        # A 500 tells QStash to hold the message and retry it according to the retry schedule
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
