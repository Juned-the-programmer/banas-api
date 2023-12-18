from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, CustomerAccount
from django.conf import settings
from django.utils.html import strip_tags
from .task import send_async_email
from dailyentry.models import customer_daily_entry_monthly
# from dailyentry.task import generate_customer_qr_code_for_daily_entry_async
import qrcode
from dailyentry.models import customer_qr_code
import os

@receiver(post_save, sender=Customer)
def create_user(sender, instance, created, **kwarg):
    if created:
        if instance.email:
            username = instance.first_name.lower() +'_'+ instance.last_name.lower()
            user = User.objects.create(username=username , email=instance.email, first_name=instance.first_name, last_name=instance.last_name)
            user.set_password("banaswater")
            user.save()
            user_detail = User.objects.get(username=username)
            customer_detail = Customer.objects.get(email=instance.email)
            customer_detail.user = user_detail
            customer_detail.save()
            subject = 'Account Created'
            customer_username = user.username
            customer_password = "banaswater"
            html_message = render_to_string("customer/JoinCustomer.html", {'first_name' : instance.first_name, 'last_name' : instance.last_name , 'username' : customer_username, 'password' : customer_password})
            plain_text = strip_tags(html_message)
            # send_async_email.delay(subject, plain_text, settings.EMAIL_HOST_USER, [instance.email], html_message)
            # send_mail(subject=subject, message=plain_text, from_email=settings.EMAIL_HOST_USER, recipient_list=[instance.email], html_message=message , fail_silently=False)
        else:
            username = instance.first_name.lower() + instance.last_name.lower()
            user = User.objects.create(username=username, first_name=instance.first_name, last_name=instance.last_name)
            user.set_password("banaswater")
            user.save()
            user_detail = User.objects.get(username=username)
            customer_detail = Customer.objects.get(first_name=instance.first_name, last_name=instance.last_name)
            customer_detail.user = user_detail
            customer_detail.save()
            
@receiver(post_save, sender=Customer)
def customer_account(sender , instance , created , **kwargs):
    if created:
        CustomerAccount.objects.create(customer_name = instance, addedby="Signals")

@receiver(post_save, sender=Customer)
def customer_daily_entry(sender, instance, created, **kwargs):
    if created:
        customer_daily_entry_monthly.objects.create(customer = instance)

@receiver(post_save, sender=Customer)
def customer_daily_entry_QR(sender, instance, created, **kwargs):
    if created:
        customer_detail = Customer.objects.get(first_name=instance.first_name, last_name=instance.last_name)
        redirect_url = "https://5ed5-49-205-192-126.ngrok-free.app/api/dailyentry/customer/dailyentry/"

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
        file_name = f"{instance.first_name}_{instance.last_name}_qr_code.png"
        img_path = os.path.join(img_dir, file_name)

        # Save the QR code image
        img.save(img_path)

        # Save the image to the model
        customer_qr_code.objects.create(customer = instance, qrcode=f'qr_codes/{file_name}')

post_save.connect(customer_account,sender=Customer)
post_save.connect(create_user, sender=Customer)
post_save.connect(customer_daily_entry, sender=Customer)
post_save.connect(customer_daily_entry_QR, sender=Customer)