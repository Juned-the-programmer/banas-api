import logging

from django.core.management.base import BaseCommand

from customer.whatsapp import enqueue_whatsapp_message

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Tests the Evolution API WhatsApp integration by sending a message to a specific number"

    def add_arguments(self, parser):
        parser.add_argument("phone_number", type=str, help="The phone number to send the test message to")
        parser.add_argument(
            "--message",
            type=str,
            default="Hello from Banas Water Tracker! 🚰\nThis is a test message to verify the WhatsApp integration is working.",
            help="Custom message to send (optional)",
        )

    def handle(self, *args, **options):
        phone_no = options["phone_number"]
        message = options["message"]

        self.stdout.write(self.style.WARNING(f"Submitting test WhatsApp message to {phone_no}..."))

        try:
            # We bypass the QStash webhook endpoint and test the core logic directly
            # to verify Evolution API credentials work
            self._send_direct_for_testing(phone_no, message)
            
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully sent WhatsApp test message to {phone_no}!"))
            self.stdout.write(self.style.SUCCESS("If you don't receive it, double check your Evolution API connection status in Render."))
            
            # Also enqueue it to test the QStash path (if tokens are valid locally)
            self.stdout.write(self.style.WARNING(f"\nAlso enqueueing to QStash to test the delayed webhook path..."))
            enqueue_whatsapp_message(phone_no, "(QStash Test) " + message)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send WhatsApp message: {str(e)}"))

    def _send_direct_for_testing(self, phone: str, message: str):
        """
        Tests the HTTP connection to Evolution API directly, bypassing QStash.
        This helps isolate if the issue is QStash or Evolution keys.
        """
        import requests
        from django.conf import settings
        from customer.whatsapp import format_phone_number
        
        formatted_phone = format_phone_number(phone)

        url = f"{settings.EVOLUTION_BASE_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
        headers = {
            "apikey": settings.EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "number": formatted_phone,
            "text": message
        }

        self.stdout.write(f"Connecting to Evolution API at: {url}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code >= 400:
            self.stdout.write(self.style.ERROR(f"Evolution API Error {response.status_code}: {response.text}"))
            response.raise_for_status()
