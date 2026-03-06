from django.core.cache import cache

from customer.models import Customer, CustomerAccount


def customer_cached_data():
    cache_key = "Customer"
    cache_customer_data = cache.get(cache_key)

    if cache_customer_data is None:
        customer_data = Customer.objects.all()
        cache.set(cache_key, customer_data, timeout=None)
    else:
        customer_data = cache_customer_data

    return customer_data


def total_pending_due_cached():
    """Cache the total outstanding due amount. TTL 5 min — invalidate after any payment."""
    cache_key = "total_pending_due"
    cached = cache.get(cache_key)

    if cached is None:
        cached = CustomerAccount.calculate_total_due()
        cache.set(cache_key, cached, timeout=None)

    return cached
