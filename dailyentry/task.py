from io import BytesIO
import logging
import os

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import qrcode

from customer.models import Customer
from banas.async_helpers import async_task

from .models import DailyEntry_dashboard, customer_daily_entry_monthly, customer_qr_code

logger = logging.getLogger(__name__)


@async_task("/api/customer/tasks/generate-qr/")
def generate_customer_qr_code_for_daily_entry_async(customer_id):
    """Generate QR code for customer daily entry - runs via QStash in production, thread locally"""
    customer_detail = Customer.objects.get(id=customer_id)
    base_url = getattr(settings, "BASE_URL", "").rstrip("/")
    redirect_url = f"{base_url}/api/dailyentry/customer/dailyentry/"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_url)
    qr.add_data(customer_detail.id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Create A4 canvas (in pixels)
    # A4 size at 300 DPI = 2480x3508 pixels
    a4_width, a4_height = 2480, 3508
    a4_img = Image.new("RGB", (a4_width, a4_height), "white")
    draw = ImageDraw.Draw(a4_img)

    # Add Customer Name at top center
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)  # Bold font
    except:
        font = ImageFont.load_default()

    name_text = f"{customer_detail.first_name} {customer_detail.last_name}"
    # Use textbbox instead of deprecated textsize
    bbox = draw.textbbox((0, 0), name_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (a4_width - text_w) // 2
    draw.text((text_x, 200), name_text, font=font, fill="black")

    # Resize QR code and paste in center
    qr_size = 1200  # large enough for A4
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = (a4_width - qr_size) // 2
    qr_y = (a4_height - qr_size) // 2
    a4_img.paste(qr_img, (qr_x, qr_y))

    # Save final image to memory
    buffer = BytesIO()
    a4_img.save(buffer, format="PNG")
    buffer.seek(0)

    file_name = f"{customer_detail.first_name}_{customer_detail.last_name}_qr_code.png"
    qr_codes_path = f"qr_codes/{file_name}"

    # --- Local storage (active) ---
    import os
    local_dir = os.path.join("media", "qr_codes")
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, file_name)
    with open(local_path, "wb") as f:
        f.write(buffer.getvalue())
    saved_path = qr_codes_path

    # --- S3/Backblaze storage (commented out — uncomment when ready) ---
    # saved_path = default_storage.save(qr_codes_path, ContentFile(buffer.getvalue()))

    # Save to DB
    customer_qr_code.objects.create(customer=customer_detail, qrcode=saved_path)


@async_task("/api/dailyentry/tasks/bulk-daily-entry/")
def update_customer_daily_entry_to_monthly_table_bulk(entry_data_list):
    """Bulk update customer daily entry to monthly table - runs via QStash in production, thread locally"""
    for entry in entry_data_list:
        customer_id = entry["customer_id"]
        cooler_count = entry["cooler"]
        # Use get_or_create to handle cases where the record doesn't exist
        customer_detail, _ = customer_daily_entry_monthly.objects.get_or_create(
            customer_id=customer_id,
            defaults={"coolers": 0}
        )
        customer_detail.coolers += int(cooler_count)
        customer_detail.save()

        # Update Dashboard counts
        dailyentry_dashboard = DailyEntry_dashboard.objects.first()
        if dailyentry_dashboard:
            dailyentry_dashboard.customer_count += 1
            dailyentry_dashboard.coolers_count += int(cooler_count)
            dailyentry_dashboard.save()
        else:
            # Create dashboard if it doesn't exist
            DailyEntry_dashboard.objects.create(
                customer_count=1,
                coolers_count=int(cooler_count)
            )


def reset_dailentry_dashboard_values():
    """Reset daily entry dashboard values - Django native scheduled task"""
    daily_entry_dashboard = DailyEntry_dashboard.objects.first()
    daily_entry_dashboard.customer_count = 0
    daily_entry_dashboard.coolers_count = 0
    daily_entry_dashboard.save()


def batch_processing_for_daily_entry_on_monthly_basis():
    """Batch processing for daily entry on monthly basis - Django native scheduled task"""
    now = timezone.now()
    first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_previous_month = (first_day_of_current_month - timezone.timedelta(days=1)).replace(day=1)
    table_name = f'DailyEntry_{first_day_of_previous_month.strftime("%B_%Y")}'

    # Validate table name format to prevent SQL injection
    import re

    if not re.match(r"^DailyEntry_[A-Za-z]+_\d{4}$", table_name):
        raise ValueError(f"Invalid table name format: {table_name}")

    # Custom SQL for creating a new table
    create_table_sql = f"""  # nosec
    CREATE TABLE {table_name} (
        id UUID PRIMARY KEY,
        customer_id UUID,
        cooler INTEGER,
        date_added TIMESTAMP,
        addedby VARCHAR(100),
        updatedby VARCHAR(100),
        original_entry_id UUID
    );
    """

    with connection.cursor() as cursor:
        cursor.execute(create_table_sql)

    # Insert data into the new table
    insert_sql = f"""  # nosec
    INSERT INTO {table_name} (id, customer_id, cooler, date_added, addedby, updatedby, original_entry_id)
    SELECT id, customer_id, cooler, date_added, addedby, updatedby, id
    FROM dailyentry_dailyentry;
    """

    with connection.cursor() as cursor:
        cursor.execute(insert_sql)

    # Truncate the original table to free up space
    truncate_sql = "TRUNCATE TABLE dailyentry_dailyentry RESTART IDENTITY;"

    with connection.cursor() as cursor:
        cursor.execute(truncate_sql)

    return f"Successfully processed entries into {table_name} and truncated the original table"


# -----------------------------------------------------------------------
# QStash HTTP Callback Endpoint
# -----------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def task_bulk_daily_entry(request):
    """
    QStash callback: Bulk update customer daily entry to monthly table.
    Payload: { args: [entry_data_list] }
    """
    try:
        data = request.data
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})

        entry_data_list = args[0] if args else kwargs.get("entry_data_list")
        if not entry_data_list:
            return Response({"error": "Missing entry_data_list"}, status=status.HTTP_400_BAD_REQUEST)

        update_customer_daily_entry_to_monthly_table_bulk.__wrapped__(entry_data_list)
        logger.info(f"Bulk daily entry task completed for {len(entry_data_list)} entries")
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Bulk daily entry task failed: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
