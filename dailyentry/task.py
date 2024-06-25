from celery import shared_task
import qrcode
from .models import customer_qr_code, DailyEntry_dashboard
from customer.models import Customer
from django.conf import settings
import os

@shared_task
def generate_customer_qr_code_for_daily_entry_async(customer_id):
    customer_detail = Customer.objects.get(id=customer_id)
    redirect_url = "https://3d5c-2409-40c1-502a-5efa-9d17-5e72-210e-9f28.ngrok-free.app/api/dailyentry/customer/dailyentry/"

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Adding data
    qr.add_data(redirect_url)
    qr.add_data(customer_detail.id)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to Media Folder
    img_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(img_dir, exist_ok=True)

    # Define the complete path to save the image
    file_name = f"{customer_detail.first_name}_{customer_detail.last_name}_qr_code.png"
    img_path = os.path.join(img_dir, file_name)

    # Save the QR code image
    img.save(img_path)

    # Save the image to the model
    customer_qr_code.objects.create(customer = customer_detail, qrcode=f'qr_codes/{file_name}')

@shared_task
def update_customer_daily_entry_to_monthly_table_bulk(daily_entries):
    for entry in daily_entries:
        customer_detail = customer_daily_entry_monthly.objects.get(customer=entry.customer.id)
        customer_detail.coolers += int(entry.cooler)
        customer_detail.save()

        # Update Dashboard counts
        dailyentry_dashboard = DailyEntry_dashboard.objects.first()
        dailyentry_dashboard.customer_count += 1
        dailyentry_dashboard.coolers_count += int(entry.cooler)
        dailyentry_dashboard.save()

@shared_task
def reset_dailentry_dashboard_values():
    daily_entry_dashboard = DailyEntry_dashboard.objects.first()
    daily_entry_dashboard.customer_count = 0
    daily_entry_dashboard.coolers_count = 0
    daily_entry_dashboard.save()