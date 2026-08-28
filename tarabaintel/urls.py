from django.contrib import admin
from django.urls import path, include
from insight.views import intelligence_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('insight.urls')),
    path('', intelligence_dashboard, name='dashboard'),  # <-- THIS IS THE DASHBOARD
]