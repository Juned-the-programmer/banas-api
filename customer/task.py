import datetime

from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mail


@shared_task
def send_async_email(subject, message, sender, recipient_list, html_message):
    send_mail(subject, message, sender, recipient_list, html_message)
    mail = EmailMultiAlternatives(subject, message, sender, recipient_list)
    mail.attach_alternative(html_message, "text/html")
    mail.send()


@shared_task
def heartbeat():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"✅ One-shot task executed at {now}")
    return f"One-shot task executed at {now}"
