from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import RegisterView, ProfileView
from insight.views import intelligence_briefing_dashboard
from insight.views import predictive_hotspots
from insight.views import rewards_dashboard_api



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. SPECIFIC ROUTES MUST COME FIRST!
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 2. GENERIC INCLUDE COMES LAST (so it doesn't swallow the routes above)
    path('api/', include('insight.urls')), 
    
    # Dashboard URL
    path('', intelligence_briefing_dashboard, name='dashboard'),

    # Add this import at the top with the other imports
    # Add this to the urlpatterns list
    path('api/predictive-hotspots/', predictive_hotspots, name='predictive-hotspots'),
    
    path('api/rewards/dashboard/', views.rewards_dashboard_api, name='rewards-dashboard-api'),
    
    # (Keep the HTML version for web browsers at a different URL if needed)
    path('rewards/dashboard/', views.rewards_dashboard_page, name='rewards-dashboard-web'),
]
