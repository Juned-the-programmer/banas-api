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

@async_task("/api/customer/tasks/send-email/", queue="send-email")
def send_async_email(subject, message, sender, recipient_list, html_message):
    """Send email asynchronously - runs via QStash in production, thread locally"""
    send_mail(subject, message, sender, recipient_list, html_message)
    mail = EmailMultiAlternatives(subject, message, sender, recipient_list)
    mail.attach_alternative(html_message, "text/html")
    mail.send()

@async_task("/api/customer/tasks/generate-qr/", queue="generate-qr")
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