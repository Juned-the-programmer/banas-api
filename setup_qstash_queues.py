"""
One-time script to set up QStash named queues for async tasks.
Run this after deploying to configure queues in QStash.

Usage: python setup_qstash_queues.py
"""

import os
import sys

import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banas.settings")
django.setup()

from banas.qstash import qstash_client


def setup_queues():
    if not qstash_client:
        print("❌ Error: QStash client not initialized")
        print("   Please ensure QSTASH_TOKEN is set in your environment")
        return

    # Define queues: (name, parallelism, description)
    # parallelism=1 for DB-heavy tasks (prevents race conditions)
    # parallelism>1 for I/O-bound tasks (email, QR generation)
    queues = [
        ("send-email", 2, "Send async emails (I/O bound, safe to parallelize)"),
        ("generate-qr", 2, "Generate customer QR codes (I/O bound)"),
        ("verify-pending", 1, "Verify & commit pending daily entries (DB writes, ordered)"),
        ("bulk-import", 1, "Bulk import daily entries from admin (DB writes, ordered)"),
        ("bill-batch", 1, "Process monthly bill batch per customer chunk (DB writes, ordered)"),
        ("whatsapp-messages", 1, "Paced WhatsApp messaging via Evolution API (Strictly ordered, 3s delay)"),
    ]

    print(f"🔧 Configuring {len(queues)} QStash queues...\n")

    for name, parallelism, description in queues:
        print(f"   Queue: {name}")
        print(f"   → {description}")
        print(f"   → Parallelism: {parallelism}")
        try:
            qstash_client.queue.upsert(
                queue=name,
                parallelism=parallelism,
            )
            print("   ✅ Success\n")
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")

    print("✨ Queue setup complete!")
    print("   You can now see your queues in the QStash dashboard → Queues tab.")


if __name__ == "__main__":
    setup_queues()
