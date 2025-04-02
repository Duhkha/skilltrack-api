from django.contrib import admin
from django.urls import path

from .views import HealthCheckView, CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/health/', HealthCheckView.as_view(), name='health-check'),
    path('api/login/', CustomLoginView.as_view(), name='custom-login'),
]