"""banas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from .swagger import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('authentication.urls')),
    path('api/route/',include('route.urls')),
    path('api/customer/',include('customer.urls')),
    path('api/dailyentry/', include('dailyentry.urls')),
    path('api/bill/', include('bills.urls')),
    path('api/payment/', include('payment.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('reset_password/', auth_views.PasswordResetView.as_view(),
            name="reset_password"),
    path('reset_password_send/',auth_views.PasswordResetDoneView.as_view(),
            name="password_reset_done"),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(),
            name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(),
            name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)