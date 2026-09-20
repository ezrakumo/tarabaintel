from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from accounts.views import RegisterView, ProfileView
from insight.views import (
    intelligence_briefing_dashboard,
    ReportViewSet,
    FieldVerificationViewSet,
    test_ai_engine,
    rewards_dashboard_api,
    trigger_weekly_forecast,
    predictive_hotspots,
    debug_rewards,
    RedeemRewardView
)

# ✅ 1. SETUP THE ROUTER
# This is the ONLY router that matters now.
router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'field-verifications', FieldVerificationViewSet, basename='field-verification')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ 2. AUTH ROUTES
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ✅ 3. ROUTER URLS (Generates /api/field-verifications/ AND /claim/)
    path('api/', include(router.urls)),
    
    # ✅ 4. OTHER SPECIFIC API ENDPOINTS
    path('api/rewards/redeem/', RedeemRewardView.as_view(), name='redeem-reward'),
    path('api/rewards/dashboard/', rewards_dashboard_api, name='rewards-dashboard-api'),
    path('api/cron/weekly-forecast/', trigger_weekly_forecast, name='weekly-forecast-cron'),
    path('api/predictive-hotspots/', predictive_hotspots, name='predictive-hotspots'),
    path('api/debug-rewards/', debug_rewards, name='debug-rewards'),
    path('api/test-ai/', test_ai_engine, name='test-ai'),
    
    # ✅ 5. DASHBOARD URL
    path('', intelligence_briefing_dashboard, name='dashboard'),
    
    # ✅ 6. ROUTING TEST ENDPOINT (To prove the router is working)
    path('api/test-routing/', lambda request: HttpResponse("Router is working perfectly!"), name='test-routing'),
]
