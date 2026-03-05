from datetime import datetime
import logging

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
import uuid6

from banas.cache_conf import total_pending_due_cached
from banas.qstash import qstash_client
from bills.utils import bill_number_generator
from customer.models import Customer, CustomerAccount
from customer.whatsapp import enqueue_whatsapp_message
from dailyentry.models import customer_daily_entry_monthly

from .models import CustomerBill

logger = logging.getLogger(__name__)

BILL_BATCH_SIZE = 100  # customers per QStash message
BILL_BATCH_QUEUE = "bill-batch"
WORKER_PATH = "/api/bill/tasks/process-bill-batch/"


def _chunk(lst, size):
    """Split a list into chunks of `size`."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


# -----------------------------------------------------------------------
# Dispatcher helper — contains the fan-out logic (called by the view)
# -----------------------------------------------------------------------
def dispatch_monthly_bill_batches():

    today = timezone.localdate()
    tomorrow = today + timezone.timedelta(days=1)

    if tomorrow.month == today.month:
        return {
            "skipped": True,
            "message": f"Not the last day of the month ({today})",
        }

    first_date = str(today.replace(day=1))
    last_date = str(today)

    customer_ids = list(Customer.objects.filter(active=True).values_list("id", flat=True))
    if not customer_ids:
        return {"skipped": True, "message": "No active customers"}

    # Invalidate the due cache before any batch mutates CustomerAccount.due
    cache.delete("total_pending_due")

    base_url = getattr(settings, "BASE_URL", "").rstrip("/")
    worker_url = f"{base_url}{WORKER_PATH}"

    batches_queued = 0
    chunks = list(_chunk([str(cid) for cid in customer_ids], BILL_BATCH_SIZE))

    for chunk in chunks:
        payload = {
            "customer_ids": chunk,
            "first_date": first_date,
            "last_date": last_date,
        }
        try:
            if qstash_client:
                # Named queue → ordered delivery, concurrency control, retries
                qstash_client.message.enqueue_json(
                    queue=BILL_BATCH_QUEUE,
                    url=worker_url,
                    body=payload,
                    retries=3,
                )
            else:
                # Local dev fallback — process synchronously in same thread
                process_bill_batch_core(chunk, first_date, last_date)
            batches_queued += 1
        except Exception as exc:
            logger.error(
                "dispatch_monthly_bill_batches: failed to enqueue batch %d — %s",
                batches_queued + 1,
                exc,
                exc_info=True,
            )

    logger.info(
        "Monthly bill dispatcher: %d batches queued for %s–%s",
        batches_queued,
        first_date,
        last_date,
    )
    return {
        "skipped": False,
        "batches_queued": batches_queued,
        "customers_total": len(customer_ids),
        "billing_period": {"from": first_date, "to": last_date},
    }


# -----------------------------------------------------------------------
# Worker core — the actual DB work for one batch (called by the view)
# -----------------------------------------------------------------------
def process_bill_batch_core(customer_ids, first_date, last_date):

    customers_queryset = Customer.objects.filter(id__in=customer_ids).select_related(
        "customer_account", "customer_daily_entry_monthly"
    )

    customer_map = {str(c.id): c for c in customers_queryset}

    base_bill_number = bill_number_generator()
    bill_prefix = base_bill_number[:-4]
    sequence = int(base_bill_number[-4:])

    month_name = datetime.strptime(first_date, "%Y-%m-%d").strftime("%B %Y")

    bills_to_create: list = []
    accounts_to_update: list = []
    entries_to_update: list = []

    for cid in customer_ids:
        customer = customer_map.get(str(cid))
        account = customer.customer_account
        entry = customer.customer_daily_entry_monthly

        if not customer or not account or not entry:
            logger.warning(
                "process_bill_batch_core: skipping customer %s — missing %s",
                cid,
                [name for name, obj in [("customer", customer), ("account", account), ("entry", entry)] if not obj],
            )
            continue

        coolers = entry.coolers
        rate = int(customer.rate)
        due = account.due
        sequence += 1

        bill_total = (coolers * rate) + int(due)
        bill_id = uuid6.uuid7()

        bills_to_create.append(
            CustomerBill(
                id=bill_id,
                bill_number=f"{bill_prefix}{str(sequence).zfill(4)}",
                customer_name=customer,
                from_date=first_date,
                to_date=last_date,
                coolers=coolers,
                Rate=rate,
                Amount=coolers * rate,
                Pending_amount=due,
                Advanced_amount=0,
                Total=(coolers * rate) + due,
                addedby="Automation Task",
            )
        )

        account.due = (coolers * rate) + due
        accounts_to_update.append(account)

        entry.coolers = 0
        entries_to_update.append(entry)

        # Enqueue WhatsApp Message for Bill Generation
        if customer.phone_no:
            invoice_link = f"{settings.BASE_URL.rstrip('/')}/api/bill/invoice/{bill_id}/"
            message_body = (
                f"Dear {customer.first_name} {customer.last_name},\n"
                f"Your Water Cooler bill for {month_name} has been generated.\n"
                f"Total Coolers: {coolers}\n"
                f"Previous Due: ₹{due}\n"
                f"Total Amount Payable: ₹{bill_total}\n\n"
                f"View your detailed invoice here:\n{invoice_link}\n\n"
                "Please pay at your earliest convenience."
            )
            enqueue_whatsapp_message(customer.phone_no, message_body)

    if not bills_to_create:
        logger.info("process_bill_batch_core: nothing to write for this batch.")
        return

    # ------------------------------------------------------------------
    # 3. Atomic write: 3 queries total
    # ------------------------------------------------------------------
    with transaction.atomic():
        # INSERT all bills in one round-trip
        CustomerBill.objects.bulk_create(bills_to_create, batch_size=500)

        # UPDATE due balances for all accounts in one round-trip
        CustomerAccount.objects.bulk_update(accounts_to_update, ["due"], batch_size=500)

        # RESET monthly coolers for all entries in one round-trip
        customer_daily_entry_monthly.objects.bulk_update(entries_to_update, ["coolers"], batch_size=500)

    cache.delete("total_pending_due")
    total_pending_due_cached()

    logger.info(
        "process_bill_batch_core: committed %d bills (%s – %s)",
        len(bills_to_create),
        first_date,
        last_date,
    )
