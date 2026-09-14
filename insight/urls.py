from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportViewSet, FieldVerificationViewSet,
    test_ai_engine, intelligence_briefing_dashboard
)
from .views import (
    ReportViewSet, FieldVerificationViewSet, test_ai_engine, 
    intelligence_briefing_dashboard, rewards_dashboard_page
)
from .rewards_views import (
    UserProfileViewSet, RewardLedgerViewSet,
    RewardCatalogView, RedemptionViewSet,
    MyReportsView, RewardsDashboardView
)
from django.urls import path
from .views import RedeemRewardView # Add this import

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'field-verifications', FieldVerificationViewSet, basename='field-verification')
router.register(r'rewards/profile', UserProfileViewSet, basename='user-profile')
router.register(r'rewards/ledger', RewardLedgerViewSet, basename='reward-ledger')
router.register(r'rewards/redemptions', RedemptionViewSet, basename='redemption')

urlpatterns = [
    path('', include(router.urls)),
    path('test-ai/', test_ai_engine, name='test_ai'),
    path('briefing/', intelligence_briefing_dashboard, name='intelligence_briefing'),
    path('rewards/catalog/', RewardCatalogView.as_view(), name='reward-catalog'),
    path('rewards/my-reports/', MyReportsView.as_view(), name='my-reports'),
    path('rewards/dashboard/', RewardsDashboardView.as_view(), name='rewards-dashboard'),
    path('rewards/', rewards_dashboard_page, name='rewards_dashboard_page'),
    path('rewards/redeem/', RedeemRewardView.as_view(), name='redeem-reward'),
    

]