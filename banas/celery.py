from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banas.settings')

# Create a Celery instance and configure it using the settings from Django.
app = Celery('banas')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# update Time Zone
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()

# celery beats tasks
app.conf.beat_schedule = {
    'generate_bill_on_monthly' : {
        'task' : 'bills.task.run_monthly_task',
        'schedule' : crontab(hour=23, minute=00)
    },
    'reset_dailyentry_dashboard_values': {
        'task': 'dailyentry.task.reset_dailentry_dashboard_values',
        'schedule': crontab(hour=0,minute=1),
    },
    'process_entries_every_month' : {
        'task' : 'dailyentry.task.batch_processing_for_daily_entry_ofn_monthly_basis',
        'schedule' : crontab(hour=3, day_of_month=1)
    }
}