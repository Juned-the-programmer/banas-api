import logging
import os
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from PIL import Image, ImageDraw, ImageFont
import qrcode

from banas.async_helpers import async_task
from customer.models import Customer
from dailyentry.models import customer_qr_code

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

    # Encode: "<scan_url>|<customer_id>" so the QR links to a specific customer's entry page
    redirect_url = f"{base_url}/api/dailyentry/customer/dailyentry/{customer_detail.id}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(redirect_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Create A4 canvas (2480×3508 px at 300 DPI)
    a4_width, a4_height = 2480, 3508
    a4_img = Image.new("RGB", (a4_width, a4_height), "white")
    draw = ImageDraw.Draw(a4_img)

    # 1. Font Management - Auto-download reliable TrueType font
    font_filename = "Roboto-Bold.ttf"
    font_path = os.path.join(settings.BASE_DIR, font_filename)
    if not os.path.exists(font_path):
        import urllib.request
        logger.info(f"Downloading {font_filename} from Google Fonts...")
        # Direct link to Roboto Bold TTF
        url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        try:
            urllib.request.urlretrieve(url, font_path)
            logger.info("Font downloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to download font: {e}")

    try:
        font_large = ImageFont.truetype(font_path, 180)  # Huge font for Name
        font_medium = ImageFont.truetype(font_path, 140) # Large font for Footer
    except OSError:
        logger.warning(f"Could not load {font_filename}, falling back to default tiny font.")
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # 2. Draw Customer Name (Top Centered)
    name_text = f"{customer_detail.first_name} {customer_detail.last_name}"
    bbox_name = draw.textbbox((0, 0), name_text, font=font_large)
    name_w = bbox_name[2] - bbox_name[0]
    name_x = (a4_width - name_w) // 2
    draw.text((name_x, 300), name_text, font=font_large, fill="black")

    # 3. Resize QR and paste in center
    qr_size = 1400
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = (a4_width - qr_size) // 2
    qr_y = (a4_height - qr_size) // 2
    a4_img.paste(qr_img, (qr_x, qr_y))

    # 4. Draw "Banas Water" Footer (Bottom Centered, below QR)
    footer_text = "Banas Water"
    bbox_footer = draw.textbbox((0, 0), footer_text, font=font_medium)
    footer_w = bbox_footer[2] - bbox_footer[0]
    footer_x = (a4_width - footer_w) // 2
    footer_y = qr_y + qr_size + 200 # 200px below the QR code image
    draw.text((footer_x, footer_y), footer_text, font=font_medium, fill="black")

    # Render to in-memory buffer
    buffer = BytesIO()
    a4_img.save(buffer, format="PNG")
    buffer.seek(0)

    file_name = f"{customer_detail.first_name}_{customer_detail.last_name}_qr_code.png"
    qr_codes_path = f"qr_codes/{file_name}"

    # Save to local disk under media/qr_codes/
    local_dir = os.path.join("media", "qr_codes")
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, file_name)
    with open(local_path, "wb") as f:
        f.write(buffer.getvalue())

    # Persist the reference in DB (update if already exists)
    customer_qr_code.objects.update_or_create(
        customer=customer_detail,
        defaults={"qrcode": qr_codes_path},
    )

    logger.info("QR code saved locally for customer %s → %s", customer_id, local_path)