from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, FieldVerificationViewSet, test_ai_engine
from .views import ReportViewSet, FieldVerificationViewSet, test_ai_engine, intelligence_briefing_dashboard
from .views import ReportViewSet, FieldVerificationViewSet, test_ai_engine, intelligence_briefing_dashboard, run_migrations_temp
# Initialize the API Router
router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'field-verifications', FieldVerificationViewSet, basename='field-verification')

urlpatterns = [
    # Core API Endpoints
    path('', include(router.urls)),
    
    # AI Engine Test Endpoint 
    # (Note: In final production, this should be removed or protected with IsAdminUser permissions)
    path('test-ai/', test_ai_engine, name='test_ai'),
    path('briefing/', intelligence_briefing_dashboard, name='intelligence_briefing')
    path('temp-migrate/', run_migrations_temp, name='temp_migrate'),
]