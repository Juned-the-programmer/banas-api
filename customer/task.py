from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

@shared_task
def send_async_email(subject, message, sender, recipient_list, html_message):
    send_mail(subject, message, sender, recipient_list, html_message)
    mail = EmailMultiAlternatives(subject, message, sender, recipient_list)
    mail.attach_alternative(html_message, 'text/html')
    mail.send()