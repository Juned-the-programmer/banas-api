from django.core.cache import cache

from customer.models import Customer, CustomerAccount


def customer_cached_data():
    cache_key = "Customer"
    cache_customer_data = cache.get(cache_key)

    if cache_customer_data is None:
        # Force evaluation with list() so the cache stores actual data,
        # not a lazy unevaluated QuerySet (which would hit the DB on every cache "hit").
        cache_customer_data = list(Customer.objects.select_related("route").all())
        cache.set(cache_key, cache_customer_data, timeout=None)

    # Return a QuerySet filtered from the cached IDs so callers can still chain
    # .filter(), .select_related(), etc. on the result.
    cached_ids = [c.id for c in cache_customer_data]
    return Customer.objects.filter(id__in=cached_ids)



def total_pending_due_cached():
    """Cache the total outstanding due amount. TTL 5 min — invalidate after any payment."""
    cache_key = "total_pending_due"
    cached = cache.get(cache_key)

    if cached is None:
        cached = CustomerAccount.calculate_total_due()
        cache.set(cache_key, cached, timeout=None)

    return cached
