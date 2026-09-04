from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, FieldVerificationViewSet, test_ai_engine, run_migrations_endpoint, fix_missing_tables

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'field-verifications', FieldVerificationViewSet, basename='field-verification')

urlpatterns = [
    path('', include(router.urls)),
    path('test-ai/', test_ai_engine, name='test_ai'),
    path('run-migrations/', run_migrations_endpoint, name='run_migrations'),
    path('fix-db/', fix_missing_tables, name='fix_db'),
]