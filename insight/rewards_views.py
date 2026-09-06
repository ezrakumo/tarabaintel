from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, RewardLedger, RewardCatalog, Redemption, Report
from .serializers import (
    UserProfileSerializer, RewardLedgerSerializer,
    RewardCatalogSerializer, RedemptionSerializer,
    RedeemRewardSerializer, MyReportSerializer
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


class RedemptionViewSet(viewsets.ModelViewSet):
    """
    GET /api/rewards/redemptions/ - My redemptions
    POST /api/rewards/redemptions/ - Redeem a reward
    """
    serializer_class = RedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return Redemption.objects.none()
        return Redemption.objects.filter(user_profile=profile)

    def create(self, request, *args, **kwargs):
        """Redeem a reward - atomic transaction"""
        serializer = RedeemRewardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reward_id = serializer.validated_data['reward_id']
        delivery_details = serializer.validated_data.get('delivery_details', '')

        try:
            with transaction.atomic():
                profile, created = UserProfile.objects.select_for_update().get_or_create(
                    user=request.user
                )

                try:
                    reward = RewardCatalog.objects.get(id=reward_id, is_active=True)
                except RewardCatalog.DoesNotExist:
                    return Response(
                        {'error': 'Reward not found or not available'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                if not reward.is_available:
                    return Response(
                        {'error': 'Reward is not available'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
                user_tier_idx = tier_order.index(profile.tier)
                reward_tier_idx = tier_order.index(reward.min_tier_required)
                if user_tier_idx < reward_tier_idx:
                    return Response(
                        {'error': f'Requires {reward.get_min_tier_required_display()} tier or higher'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                if profile.total_points < reward.points_required:
                    return Response(
                        {
                            'error': 'Insufficient points',
                            'required': reward.points_required,
                            'available': profile.total_points
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                profile.total_points -= reward.points_required
                profile.save()

                RewardLedger.objects.create(
                    user_profile=profile,
                    transaction_type=f'REDEEMED_{reward.category}',
                    points=-reward.points_required,
                    description=f'Redeemed: {reward.title}',
                    related_report=None
                )

                redemption = Redemption.objects.create(
                    user_profile=profile,
                    reward=reward,
                    points_deducted=reward.points_required,
                    delivery_details=delivery_details,
                    status='PENDING'
                )

                if reward.quantity_available > 0:
                    reward.quantity_available -= 1
                    reward.save()

                return Response(
                    RedemptionSerializer(redemption).data,
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
    """GET /api/rewards/dashboard/ - Complete rewards dashboard data"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        recent_ledger = RewardLedger.objects.filter(
            user_profile=profile
        )[:10]

        active_redemptions = Redemption.objects.filter(
            user_profile=profile
        ).exclude(status__in=['REJECTED', 'FULFILLED'])[:5]

        tier_order = ['CITIZEN', 'VOLUNTEER', 'INFORMANT', 'AGENT']
        user_tier_idx = tier_order.index(profile.tier)
        available_tiers = tier_order[:user_tier_idx + 1]
        available_rewards = RewardCatalog.objects.filter(
            is_active=True,
            min_tier_required__in=available_tiers,
            points_required__lte=profile.total_points
        )[:6]

        return Response({
            'profile': UserProfileSerializer(profile).data,
            'recent_transactions': RewardLedgerSerializer(recent_ledger, many=True).data,
            'active_redemptions': RedemptionSerializer(active_redemptions, many=True).data,
            'affordable_rewards': RewardCatalogSerializer(available_rewards, many=True).data,
            'next_tier': tier_order[min(user_tier_idx + 1, len(tier_order) - 1)] if user_tier_idx < 3 else None,
            'points_to_next_tier': self._points_to_next_tier(profile, tier_order)
        })

    def _points_to_next_tier(self, profile, tier_order):
        """Calculate points needed for next tier"""
        thresholds = {'CITIZEN': 0, 'VOLUNTEER': 500, 'INFORMANT': 2000, 'AGENT': 5000}
        current_idx = tier_order.index(profile.tier)
        if current_idx >= 3:
            return None
        next_tier = tier_order[current_idx + 1]
        return max(0, thresholds[next_tier] - profile.lifetime_points)