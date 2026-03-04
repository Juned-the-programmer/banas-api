"""
One-time script to set up QStash scheduled tasks.
Run this after deploying to configure recurring schedules in QStash.

Usage: python setup_qstash_schedules.py
"""

import os
import sys

import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banas.settings")
django.setup()

from django.conf import settings

from banas.qstash import qstash_client


def setup_schedules():
    if not qstash_client:
        print("❌ Error: QStash client not initialized")
        print("   Please ensure QSTASH_TOKEN is set in your environment")
        return

    base_url = getattr(settings, "BASE_URL", "").rstrip("/")
    if not base_url:
        print("❌ Error: BASE_URL is not set in settings or .env")
        print("   Please set BASE_URL to your public domain (e.g. https://banas.up.railway.app)")
        return

    print(f"🔗 Base URL: {base_url}")

    # Define schedules: (Endpoint, Cron, Description)
    schedules = [
        (
            f"{base_url}/api/bill/tasks/monthly-bill-check/",
            "0 23 28-31 * *",
            "Monthly Bill Dispatcher (Days 28-31 at 23:00 — fans out to bill-batch queue)",
        ),
        (f"{base_url}/api/dailyentry/tasks/reset-dashboard/", "1 0 * * *", "Reset Dashboard Counters (Daily at 00:01)"),
    ]

    print(f"📅 Configuring {len(schedules)} schedules...")

    for url, cron, description in schedules:
        print(f"   Setting up: {description}")
        print(f"   → {url}")
        try:
            # Create schedule using QStash SDK
            qstash_client.schedule.create(
                destination=url,
                cron=cron,
                retries=3,
                headers={"Upstash-Timezone": "Asia/Kolkata"},
            )
            print(f"   ✅ Success\n")
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")

    print("✨ Setup complete!")


if __name__ == "__main__":
    setup_schedules()
