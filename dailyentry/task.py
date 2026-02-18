from io import BytesIO
import logging
import os

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import qrcode

from customer.models import Customer
from banas.async_helpers import async_task

from .models import DailyEntry_dashboard, customer_daily_entry_monthly, customer_qr_code

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Reset daily entry dashboard values
# -----------------------------------------------------------------------
def reset_dailentry_dashboard_values():
    """Reset daily entry dashboard values - Django native scheduled task"""
    daily_entry_dashboard = DailyEntry_dashboard.objects.first()
    daily_entry_dashboard.customer_count = 0
    daily_entry_dashboard.coolers_count = 0
    daily_entry_dashboard.save()

# -----------------------------------------------------------------------
# Batch processing for daily entry on monthly basis
# -----------------------------------------------------------------------
def batch_processing_for_daily_entry_on_monthly_basis():
    """Batch processing for daily entry on monthly basis - Django native scheduled task"""
    now = timezone.now()
    first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_previous_month = (first_day_of_current_month - timezone.timedelta(days=1)).replace(day=1)
    table_name = f'DailyEntry_{first_day_of_previous_month.strftime("%B_%Y")}'

    # Validate table name format to prevent SQL injection
    import re

    if not re.match(r"^DailyEntry_[A-Za-z]+_\d{4}$", table_name):
        raise ValueError(f"Invalid table name format: {table_name}")

    # Custom SQL for creating a new table
    create_table_sql = f"""  # nosec
    CREATE TABLE {table_name} (
        id UUID PRIMARY KEY,
        customer_id UUID,
        cooler INTEGER,
        date_added TIMESTAMP,
        addedby VARCHAR(100),
        updatedby VARCHAR(100),
        original_entry_id UUID
    );
    """

    with connection.cursor() as cursor:
        cursor.execute(create_table_sql)

    # Insert data into the new table
    insert_sql = f"""  # nosec
    INSERT INTO {table_name} (id, customer_id, cooler, date_added, addedby, updatedby, original_entry_id)
    SELECT id, customer_id, cooler, date_added, addedby, updatedby, id
    FROM dailyentry_dailyentry;
    """

    with connection.cursor() as cursor:
        cursor.execute(insert_sql)

    # Truncate the original table to free up space
    truncate_sql = "TRUNCATE TABLE dailyentry_dailyentry RESTART IDENTITY;"

    with connection.cursor() as cursor:
        cursor.execute(truncate_sql)

    return f"Successfully processed entries into {table_name} and truncated the original table"


# -----------------------------------------------------------------------
#  Verify & Commit Pending Entries (triggered by VerifyPendingDailyEntryView)
# -----------------------------------------------------------------------
@async_task("/api/dailyentry/tasks/verify-pending/")
def verify_and_commit_pending_entries(entries):
    """
    Verifies pending daily entries submitted via QR scan:
    - Creates DailyEntry records (addedby = customer name)
    - Deletes the pending_daily_entry records
    - Updates customer_daily_entry_monthly cooler counts
    - Updates DailyEntry_dashboard
    Payload: [{ id, customer, coolers, date_added }, ...]
    """
    from .models import DailyEntry, pending_daily_entry

    daily_entries = []
    pending_ids = []

    for item in entries:
        pending_ids.append(item["id"])
        customer = Customer.objects.get(id=item["customer"])
        daily_entries.append(
            DailyEntry(
                customer=customer,
                cooler=item["coolers"],
                addedby=f"{customer.first_name} {customer.last_name}",
                date_added=item["date_added"],
            )
        )

    if daily_entries:
        DailyEntry.objects.bulk_create(daily_entries)
        pending_daily_entry.objects.filter(id__in=pending_ids).delete()
        _update_monthly_and_dashboard(daily_entries)

    logger.info(f"verify_and_commit_pending_entries: committed {len(daily_entries)} entries")


# -----------------------------------------------------------------------
# Bulk Import Daily Entries (triggered by DailyEntryBulkImportView)
# -----------------------------------------------------------------------
@async_task("/api/dailyentry/tasks/bulk-import/")
def bulk_import_daily_entries(entries):
    """
    Directly imports daily entries from admin:
    - Creates DailyEntry records (addedby = "admin")
    - Updates customer_daily_entry_monthly cooler counts
    - Updates DailyEntry_dashboard
    Payload: [{ customer, cooler }, ...]
    """
    from .models import DailyEntry

    daily_entries = [
        DailyEntry(
            customer=Customer.objects.get(id=item["customer"]),
            cooler=item["cooler"],
            addedby="admin",
            date_added=timezone.now(),
        )
        for item in entries
    ]

    DailyEntry.objects.bulk_create(daily_entries)
    _update_monthly_and_dashboard(daily_entries)

    logger.info(f"bulk_import_daily_entries: imported {len(daily_entries)} entries")


# -----------------------------------------------------------------------
# Shared helper: update monthly table + dashboard
# -----------------------------------------------------------------------
def _update_monthly_and_dashboard(daily_entries):
    """Update customer_daily_entry_monthly and DailyEntry_dashboard for a list of DailyEntry objects."""
    for entry in daily_entries:
        customer_detail, _ = customer_daily_entry_monthly.objects.get_or_create(
            customer=entry.customer,
            defaults={"coolers": 0}
        )
        customer_detail.coolers += int(entry.cooler)
        customer_detail.save()

    dashboard = DailyEntry_dashboard.objects.first()
    if dashboard:
        dashboard.customer_count += len(daily_entries)
        dashboard.coolers_count += sum(int(e.cooler) for e in daily_entries)
        dashboard.save()
    else:
        DailyEntry_dashboard.objects.create(
            customer_count=len(daily_entries),
            coolers_count=sum(int(e.cooler) for e in daily_entries)
        )