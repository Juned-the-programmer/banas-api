from celery import shared_task
import qrcode
from .models import customer_qr_code
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile

@shared_task
def generate_customer_qr_code_for_daily_entry_async(customer):
    customer_detail = Customer.objects.get(first_name=customer.first_name, last_name=customer.last_name)
    redirect_url = ""

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Adding data
    qr.add_data(redirect_url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to the model
    file_name = f"{customer.first_name}_{customer.last_name}_qr_code.png"
    customer_qr_code.objects.create(customer=customer_detail)
    image_io = BytesIO()
    img.save(image_io, format='PNG')
    customer_qr_code.image.save(file_name, ContentFile(image_io.getvalue()), save=True)