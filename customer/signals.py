import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import qrcode

from dailyentry.models import customer_daily_entry_monthly, customer_qr_code
from dailyentry.task import generate_customer_qr_code_for_daily_entry_async

from .models import Customer, CustomerAccount
from .task import send_async_email


@receiver(post_save, sender=Customer)
def create_user(sender, instance, created, **kwarg):
    if created:
        if instance.email:
            username = instance.first_name.lower() + "_" + instance.last_name.lower()
            user = User.objects.create(
                username=username, email=instance.email, first_name=instance.first_name, last_name=instance.last_name
            )
            user.set_password("banaswater")
            user.save()
            user_detail = User.objects.get(username=username)
            instance.user = user_detail
            instance.save()
            subject = "Account Created"
            customer_username = user.username
            customer_password = "banaswater"
            html_message = render_to_string(
                "customer/JoinCustomer.html",
                {
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "username": customer_username,
                    "password": customer_password,
                },
            )
            plain_text = strip_tags(html_message)
            send_async_email.delay(
                subject, plain_text, settings.EMAIL_HOST_USER, [instance.email], html_message
            )  # Use this to send mail in async way.
            # send_mail(subject=subject, message=plain_text, from_email=settings.EMAIL_HOST_USER, recipient_list=[instance.email], html_message=message , fail_silently=False)
        else:
            username = instance.first_name.lower() + instance.last_name.lower()
            user = User.objects.create(username=username, first_name=instance.first_name, last_name=instance.last_name)
            user.set_password("banaswater")
            user.save()
            user_detail = User.objects.get(username=username)
            instance.user = user_detail
            instance.save()


@receiver(post_save, sender=Customer)
def customer_account(sender, instance, created, **kwargs):
    if created:
        CustomerAccount.objects.create(customer_name=instance, addedby="Signals")


@receiver(post_save, sender=Customer)
def customer_daily_entry(sender, instance, created, **kwargs):
    if created:
        customer_daily_entry_monthly.objects.create(customer=instance)


@receiver(post_save, sender=Customer)
def customer_daily_entry_QR(sender, instance, created, **kwargs):
    if created:
        generate_customer_qr_code_for_daily_entry_async.delay(instance.id)


post_save.connect(customer_account, sender=Customer)
post_save.connect(create_user, sender=Customer)
post_save.connect(customer_daily_entry, sender=Customer)
post_save.connect(customer_daily_entry_QR, sender=Customer)
