"""
WSGI config for banas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import newrelic.agent

if os.environ.get("NEW_RELIC_LICENSE_KEY"):
    newrelic.agent.initialize()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banas.settings")

application = get_wsgi_application()

if os.environ.get("NEW_RELIC_LICENSE_KEY"):
    application = newrelic.agent.wsgi_application()(application)
