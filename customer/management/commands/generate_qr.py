from django.core.management.base import BaseCommand
from customer.models import Customer
from dailyentry.task import generate_customer_qr_code_for_daily_entry_async


class Command(BaseCommand):
    help = "Generate QR code for a given customer ID"

    def add_arguments(self, parser):
        parser.add_argument("customer_id", type=str, help="UUID of the customer")

    def handle(self, *args, **options):
        customer_id = options["customer_id"]

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Customer with ID {customer_id} does not exist"))
            return

        self.stdout.write(self.style.SUCCESS(f"🔄 Generating QR code for {customer} (ID {customer_id})..."))

        result = generate_customer_qr_code_for_daily_entry_async(customer_id)

        self.stdout.write(self.style.SUCCESS(f"✅ QR code generated for {customer} (ID {customer_id})"))