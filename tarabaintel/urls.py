from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

# ✅ 1. IMPORT ALL VIEWS
from insight.views import (
    AgentRegistrationRequestView, AgentApprovalView,
    intelligence_briefing_dashboard, ReportViewSet, FieldVerificationViewSet,
    test_ai_engine, rewards_dashboard_api, trigger_weekly_forecast,
    predictive_hotspots, debug_rewards, RedeemRewardView,
    agent_performance_analytics, generate_intelligence_briefing,
    stakeholder_dashboard
)

# ✅ 2. SAFE IMPORT FOR ACCOUNTS APP
try:
    from accounts.views import RegisterView, ProfileView
    HAS_ACCOUNTS_APP = True
except ImportError:
    HAS_ACCOUNTS_APP = False

# ✅ 3. SETUP THE ROUTER
router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'field-verifications', FieldVerificationViewSet, basename='field-verification')

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),
    
    # ✅ 4. AUTH ROUTES (Includes BOTH paths for Flutter compatibility)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_login_legacy'), # ✅ Flutter app needs this!
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_legacy'),
    
    # ✅ 5. ROUTER URLS
    path('api/', include(router.urls)),
    
    # ✅ 6. REWARDS & UTILITIES
    path('api/rewards/redeem/', RedeemRewardView.as_view(), name='redeem-reward'),
    path('api/rewards/dashboard/', rewards_dashboard_api, name='rewards-dashboard-api'),
    path('api/debug-rewards/', debug_rewards, name='debug-rewards'),
    
    # ✅ 7. AI & PREDICTIONS
    path('api/cron/weekly-forecast/', trigger_weekly_forecast, name='weekly-forecast-cron'),
    path('api/predictive-hotspots/', predictive_hotspots, name='predictive-hotspots'),
    path('api/test-ai/', test_ai_engine, name='test-ai'),
    
    # ✅ 8. ANALYTICS & INTELLIGENCE
    path('api/analytics/agent-performance/', agent_performance_analytics, name='agent-performance'),
    path('api/intelligence/briefing/', generate_intelligence_briefing, name='intelligence-briefing'),
    path('api/intelligence/stakeholder-dashboard/', stakeholder_dashboard, name='stakeholder-dashboard'),
    
    # ✅ 9. AGENT REGISTRATION
    path('api/agents/register/', AgentRegistrationRequestView.as_view(), name='agent-register'),
    path('api/agents/approve/', AgentApprovalView.as_view(), name='agent-approve'),
    
    # ✅ 10. MAIN DASHBOARD
    path('', intelligence_briefing_dashboard, name='dashboard'),
]

# ✅ 11. CONDITIONALLY ADD ACCOUNTS ROUTES
if HAS_ACCOUNTS_APP:
    urlpatterns += [
        path('api/auth/register/', RegisterView.as_view(), name='register'),
        path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    ]