import datetime
import logging

from django.core.mail import EmailMultiAlternatives, send_mail
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from banas.async_helpers import async_task

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Async Task (triggered by signals)
# -----------------------------------------------------------------------

@async_task("/api/customer/tasks/send-email/")
def send_async_email(subject, message, sender, recipient_list, html_message):
    """Send email asynchronously - runs via QStash in production, thread locally"""
    send_mail(subject, message, sender, recipient_list, html_message)
    mail = EmailMultiAlternatives(subject, message, sender, recipient_list)
    mail.attach_alternative(html_message, "text/html")
    mail.send()


# -----------------------------------------------------------------------
# QStash HTTP Callback Endpoint
# -----------------------------------------------------------------------

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

        subject      = args[0] if len(args) > 0 else kwargs.get("subject")
        message      = args[1] if len(args) > 1 else kwargs.get("message")
        sender       = args[2] if len(args) > 2 else kwargs.get("sender")
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
    from dailyentry.task import generate_customer_qr_code_for_daily_entry_async

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