from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
from customer.task import heartbeat

class CustomerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customer'
    
    def ready(self):
        import customer.signals
        heartbeat.apply_async(countdown=300)