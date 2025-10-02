from django.core.cache import cache

from customer.models import *


def customer_cached_data():
    cache_key = "Customer"
    cache_customer_data = cache.get(cache_key)

    if cache_customer_data is None:
        customer_data = Customer.objects.all()
        cache.set(cache_key, customer_data, timeout=None)
    else:
        customer_data = cache_customer_data

    return customer_data
