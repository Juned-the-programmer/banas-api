import os
from io import BytesIO

import qrcode
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.db import connection
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from customer.models import Customer

from .models import DailyEntry_dashboard, customer_daily_entry_monthly, customer_qr_code


@shared_task
def generate_customer_qr_code_for_daily_entry_async(customer_id):
    customer_detail = Customer.objects.get(id=customer_id)
    redirect_url = "https://banas.up.railway.app/api/dailyentry/customer/dailyentry/"

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
    text_w, text_h = draw.textsize(name_text, font=font)
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

    # Save using default storage (S3 or local)
    file_name = f"{customer_detail.first_name}_{customer_detail.last_name}_qr_code.png"
    qr_codes_path = os.path.join("qr_codes", file_name)
    saved_path = default_storage.save(qr_codes_path, ContentFile(buffer.read()))

    # Save to DB
    customer_qr_code.objects.create(customer=customer_detail, qrcode=saved_path)


@shared_task
def update_customer_daily_entry_to_monthly_table_bulk(entry_data_list):
    for entry in entry_data_list:
        customer_id = entry["customer_id"]
        cooler_count = entry["cooler"]
        customer_detail = customer_daily_entry_monthly.objects.get(customer=customer_id)
        customer_detail.coolers += int(cooler_count)
        customer_detail.save()

        # Update Dashboard counts
        dailyentry_dashboard = DailyEntry_dashboard.objects.first()
        dailyentry_dashboard.customer_count += 1
        dailyentry_dashboard.coolers_count += int(cooler_count)
        dailyentry_dashboard.save()


@shared_task
def reset_dailentry_dashboard_values():
    daily_entry_dashboard = DailyEntry_dashboard.objects.first()
    daily_entry_dashboard.customer_count = 0
    daily_entry_dashboard.coolers_count = 0
    daily_entry_dashboard.save()


@shared_task
def batch_processing_for_daily_entry_ofn_monthly_basis():
    now = timezone.now()
    first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_previous_month = (first_day_of_current_month - timezone.timedelta(days=1)).replace(day=1)
    table_name = f'DailyEntry_{first_day_of_previous_month.strftime("%B_%Y")}'

    # Custom SQL for creating a new table
    create_table_sql = f"""
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
    insert_sql = f"""
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
