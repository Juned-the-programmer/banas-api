import datetime

from django.core.mail import EmailMultiAlternatives, send_mail

from banas.async_helpers import async_task


@async_task
def send_async_email(subject, message, sender, recipient_list, html_message):
    """Send email asynchronously using Django's native task system"""
    send_mail(subject, message, sender, recipient_list, html_message)
    mail = EmailMultiAlternatives(subject, message, sender, recipient_list)
    mail.attach_alternative(html_message, "text/html")
    mail.send()


# Heartbeat task removed - no longer needed with QStash