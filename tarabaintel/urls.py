from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import RegisterView, ProfileView
from insight.views import intelligence_briefing_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('insight.urls')), 
    
    # Authentication URLs (THESE MUST BE HERE)
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    
    # Dashboard URL
    path('', intelligence_briefing_dashboard, name='dashboard'),
]