from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, FieldVerificationViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'field-verifications', FieldVerificationViewSet, basename='field-verification')

urlpatterns = [
    path('', include(router.urls)),
]