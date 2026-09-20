from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import rewards_views

# 1. Register ViewSets
router = DefaultRouter()
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'field-verifications', views.FieldVerificationViewSet, basename='field-verification')
router.register(r'rewards/profile', rewards_views.UserProfileViewSet, basename='user-profile')
router.register(r'rewards/ledger', rewards_views.RewardLedgerViewSet, basename='reward-ledger')
# ✅ REMOVED: RedemptionViewSet (model doesn't exist)

# 2. Define URL Patterns (No duplicates!)
urlpatterns = [
    # Include all router URLs
    path('', include(router.urls)),
    
    # AI & Briefing Endpoints
    path('test-ai/', views.test_ai_engine, name='test_ai'),
    path('briefing/', views.intelligence_briefing_dashboard, name='intelligence_briefing'),
    
    # Rewards Endpoints
    path('rewards/catalog/', rewards_views.RewardCatalogView.as_view(), name='reward-catalog'),
    path('rewards/my-reports/', rewards_views.MyReportsView.as_view(), name='my-reports'),
    path('rewards/dashboard/', rewards_views.RewardsDashboardView.as_view(), name='rewards-dashboard'),
    path('rewards/page/', views.rewards_dashboard_page, name='rewards_dashboard_page'),
    
    # Redemption Endpoint (Lives in views.py)
    path('rewards/redeem/', views.RedeemRewardView.as_view(), name='redeem-reward'),
    path('debug/rewards/', views.debug_rewards, name='debug_rewards'),
]
