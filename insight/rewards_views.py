from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, RewardLedger, RewardCatalog, Report
from .serializers import (
    UserProfileSerializer, RewardLedgerSerializer,
    RewardCatalogSerializer, MyReportSerializer,
    DashboardLedgerSerializer, DashboardRewardSerializer
)

class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/rewards/profile/ - View my profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class RewardLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/rewards/ledger/ - View my transaction history"""
    serializer_class = RewardLedgerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return RewardLedger.objects.none()
        return RewardLedger.objects.filter(user_profile=profile)


class RewardCatalogView(APIView):
    """GET /api/rewards/catalog/ - List available rewards"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        catalog = RewardCatalog.objects.filter(is_active=True)

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
                user_tier_idx = tier_order.index(profile.tier)
                available_tiers = tier_order[:user_tier_idx + 1]
                catalog = catalog.filter(min_tier_required__in=available_tiers)
            except UserProfile.DoesNotExist:
                pass

        serializer = RewardCatalogSerializer(catalog, many=True)
        return Response(serializer.data)


class MyReportsView(APIView):
    """GET /api/rewards/my-reports/ - My submitted reports with scores"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reports = Report.objects.filter(
            submitted_by=request.user
        ).order_by('-submitted_at')[:50]

        serializer = MyReportSerializer(reports, many=True)

        total_reports = reports.count()
        total_points_earned = sum(r.points_awarded for r in reports if r.points_awarded)
        avg_quality = (
            sum(r.intel_quality_score for r in reports if r.intel_quality_score) / total_reports
            if total_reports > 0 else 0
        )

        return Response({
            'reports': serializer.data,
            'summary': {
                'total_reports': total_reports,
                'total_points_earned': total_points_earned,
                'average_quality_score': round(avg_quality, 1)
            }
        })


class RewardsDashboardView(APIView):
    """
    GET /api/rewards/dashboard/
    Secure endpoint requiring JWT. Accessible to all verified tiers.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # 2. Fetch Data
        recent_ledger = RewardLedger.objects.filter(user_profile=profile)[:10]
        
        # 3. Filter rewards by tier and affordability
        tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
        user_tier_idx = tier_order.index(profile.tier)
        available_tiers = tier_order[:user_tier_idx + 1]
        
        affordable_rewards = RewardCatalog.objects.filter(
            is_active=True,
            min_tier_required__in=available_tiers,
            points_required__lte=profile.total_points
        )[:6]

        # 4. Calculate Next Tier
        next_tier, points_to_next = self._calculate_next_tier(profile, tier_order)

        # 5. Build Payload (Removed active_redemptions to prevent crashes)
        dashboard_data = {
            'profile': UserProfileSerializer(profile).data,
            'recent_transactions': DashboardLedgerSerializer(recent_ledger, many=True).data,
            'affordable_rewards': DashboardRewardSerializer(affordable_rewards, many=True).data,
            'next_tier': next_tier,
            'points_to_next_tier': points_to_next
        }

        return Response(dashboard_data)

    def _calculate_next_tier(self, profile, tier_order):
        thresholds = {'Citizen': 0, 'Volunteer': 500, 'Informant': 2000, 'Agent': 5000}
        current_idx = tier_order.index(profile.tier)
        
        if current_idx >= 3: # Already max tier
            return None, None
            
        next_tier = tier_order[current_idx + 1]
        points_needed = max(0, thresholds[next_tier] - profile.lifetime_points)
        return next_tier, points_needed