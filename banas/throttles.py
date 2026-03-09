from rest_framework.throttling import ScopedRateThrottle


class QStashCallbackThrottle(ScopedRateThrottle):
    """
    Throttle for QStash callback endpoints (AllowAny, public).
    Applies the 'qstash_callback' rate scope defined in settings.
    Prevents abuse of public QStash task endpoints.
    """

    scope = "qstash_callback"
