from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

# ✅ 1. IMPORT ALL VIEWS CLEANLY
from insight.views import (
    AgentRegistrationRequestView, 
    AgentApprovalView,
    intelligence_briefing_dashboard, 
    ReportViewSet, 
    FieldVerificationViewSet,
    test_ai_engine, 
    rewards_dashboard_api, 
    trigger_weekly_forecast,
    predictive_hotspots, 
    debug_rewards, 
    RedeemRewardView,
    agent_performance_analytics, 
    generate_intelligence_briefing,
    stakeholder_dashboard, 
    trigger_ai_sitrep, 
    test_bare_metal,
    agent_leaderboard, # ✅ ADDED
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

# ✅ 4. UNIFIED URL PATTERNS
urlpatterns = [
    # ADMIN & GRAPPELLI (Grappelli MUST be before admin)
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    
    # AUTH ROUTES
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_login_legacy'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_legacy'),
    
    # ROUTER URLS
    path('api/', include(router.urls)),
    
    # REWARDS & UTILITIES
    path('api/rewards/redeem/', RedeemRewardView.as_view(), name='redeem-reward'),
    path('api/rewards/dashboard/', rewards_dashboard_api, name='rewards-dashboard-api'),
    path('api/debug-rewards/', debug_rewards, name='debug-rewards'),
    
    # AI & PREDICTIONS
    path('api/cron/weekly-forecast/', trigger_weekly_forecast, name='weekly-forecast-cron'),
    path('api/predictive-hotspots/', predictive_hotspots, name='predictive-hotspots'),
    path('api/test-ai/', test_ai_engine, name='test-ai'),
    
    # ANALYTICS & INTELLIGENCE
    path('api/analytics/agent-performance/', agent_performance_analytics, name='agent-performance'),
    path('api/analytics/leaderboard/', agent_leaderboard, name='agent-leaderboard'), # ✅ ADDED
    path('api/intelligence/briefing/', generate_intelligence_briefing, name='intelligence-briefing'),
    path('api/intelligence/stakeholder-dashboard/', stakeholder_dashboard, name='stakeholder-dashboard'),
    path('api/intelligence/generate-sitrep/', trigger_ai_sitrep, name='generate-sitrep'),
    
    # AGENT REGISTRATION
    path('api/agents/register/', AgentRegistrationRequestView.as_view(), name='agent-register'),
    path('api/agents/approve/', AgentApprovalView.as_view(), name='agent-approve'),
    
    # MAIN DASHBOARD
    path('', intelligence_briefing_dashboard, name='dashboard'),

    # BARE METAL TEST
    path('api/test-bare-metal/', test_bare_metal, name='test-bare-metal'),
]

# ✅ 5. CONDITIONALLY ADD ACCOUNTS ROUTES
if HAS_ACCOUNTS_APP:
    urlpatterns += [
        path('api/auth/register/', RegisterView.as_view(), name='register'),
        path('api/auth/profile/', ProfileView.as_view(), name='profile'),
    ]