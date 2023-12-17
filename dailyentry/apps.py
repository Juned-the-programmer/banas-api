from django.apps import AppConfig


class DailyentryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dailyentry'

    def ready(self):
        import dailyentry.signals