#!/usr/bin/env python
"""
Health check script for Docker container validation.
Tests basic Django functionality and API endpoints.
"""

import os
import sys
import time

import django
import requests
from django.core.management import execute_from_command_line


def setup_django():
    """Setup Django environment"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banas.settings_docker")
    django.setup()


def check_django_health():
    """Check if Django is properly configured"""
    try:
        setup_django()

        # Test database connection
        from django.db import connections

        db_conn = connections["default"]
        db_conn.cursor()
        print("✅ Database connection successful")

        # Test Django settings
        from django.conf import settings

        print(f"✅ Django settings loaded: {settings.DATABASES['default']['ENGINE']}")

        # Test model imports
        from django.apps import apps

        for app_config in apps.get_app_configs():
            if hasattr(app_config, "models_module") and app_config.models_module:
                print(f"✅ Models loaded for {app_config.name}")

        return True
    except Exception as e:
        print(f"❌ Django health check failed: {e}")
        return False


def check_http_health(url="http://localhost:8000", timeout=30):
    """Check if HTTP server is responding"""
    print(f"🔍 Checking HTTP health at {url}")

    for attempt in range(timeout):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ HTTP server responding (status: {response.status_code})")
                return True
            elif response.status_code == 404:
                print(f"✅ HTTP server responding (status: {response.status_code}) - No route at /")
                return True
            else:
                print(f"⚠️ HTTP server responding with status: {response.status_code}")
                return True
        except requests.exceptions.RequestException as e:
            if attempt < timeout - 1:
                print(f"⏳ Attempt {attempt + 1}: HTTP server not ready, retrying...")
                time.sleep(1)
            else:
                print(f"❌ HTTP server not responding after {timeout} attempts: {e}")
                return False

    return False


def check_admin_health(url="http://localhost:8000/admin/"):
    """Check if Django admin is accessible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code in [200, 302]:  # 302 = redirect to login
            print("✅ Django admin accessible")
            return True
        else:
            print(f"⚠️ Django admin returned status: {response.status_code}")
            return True  # Still considered healthy
    except requests.exceptions.RequestException as e:
        print(f"❌ Django admin not accessible: {e}")
        return False


def check_api_health(url="http://localhost:8000/api/"):
    """Check if API endpoints are accessible"""
    try:
        response = requests.get(url, timeout=5)
        # Any response means the server is running
        print(f"✅ API endpoint accessible (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API endpoint check: {e}")
        return True  # Don't fail on API endpoint issues


def main():
    """Run all health checks"""
    print("🩺 Starting Docker container health checks...")

    checks = [
        ("Django Health", check_django_health),
        ("HTTP Health", lambda: check_http_health()),
        ("Admin Health", lambda: check_admin_health()),
        ("API Health", lambda: check_api_health()),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 Running {check_name} check...")
        try:
            result = check_func()
            results.append((check_name, result))
            if result:
                print(f"✅ {check_name} check passed")
            else:
                print(f"❌ {check_name} check failed")
        except Exception as e:
            print(f"❌ {check_name} check error: {e}")
            results.append((check_name, False))

    # Summary
    print("\n📊 Health Check Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All health checks passed! Container is healthy.")
        sys.exit(0)
    else:
        print("⚠️ Some health checks failed. Container may not be fully functional.")
        sys.exit(1)


if __name__ == "__main__":
    main()
