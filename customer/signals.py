from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, CustomerAccount
from django.conf import settings

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
            message = 'Your account has been created. Welcome!\n\nUsername : {}\n Password : {}'.format(customer_username, customer_password)
            send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.email], fail_silently=False)
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


post_save.connect(customer_account,sender=Customer)
post_save.connect(create_user, sender=Customer)