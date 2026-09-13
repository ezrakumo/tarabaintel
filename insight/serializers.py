from rest_framework import serializers
from .models import (
    Report, FieldAgent, FieldVerification, LGA, RewardLedger, Redemption
)
from .models import UserProfile
from .models import RewardCatalog # Ensure this is at the top of your file


# ==========================================
# CORE SERIALIZERS
# ==========================================

class LGASerializer(serializers.ModelSerializer):
    class Meta:
        model = LGA
        fields = ['id', 'name', 'state', 'population']


class ReportSerializer(serializers.ModelSerializer):
    lga_name = serializers.CharField(source='lga.name', read_only=True, default='Unknown')

    class Meta:
        model = Report
        fields = [
            'id', 'description', 'issue_category', 'status',
            'location', 'lga', 'lga_name', 'image_base64',
            'submitted_at', 'submitted_by',
            'ai_suggested_category', 'ai_confidence_score',
            'ai_sentiment', 'ai_urgency_level', 'ai_extracted_entities',
            'is_covert', 'intel_quality_score', 'points_awarded',
            'acknowledgment_sent'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'ai_suggested_category',
            'ai_confidence_score', 'ai_sentiment', 'ai_urgency_level',
            'ai_extracted_entities', 'intel_quality_score',
            'points_awarded', 'acknowledgment_sent'
        ]


class FieldAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldAgent
        fields = ['id', 'agent_id', 'name', 'is_active', 'assigned_lga']


class FieldVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldVerification
        fields = [
            'id', 'report', 'assigned_agent', 'status',
            'assigned_at', 'claimed_at', 'verified_at',
            'notes', 'is_valid'
        ]
        read_only_fields = ['id', 'assigned_at', 'claimed_at', 'verified_at']


class VerificationClaimSerializer(serializers.Serializer):
    agent_id = serializers.CharField()


class VerificationCompleteSerializer(serializers.Serializer):
    agent_id = serializers.CharField()
    is_valid = serializers.BooleanField()
    notes = serializers.CharField(required=False, allow_blank=True)


# ==========================================
# TARABAINSIGHT 2.0: REWARD SERIALIZERS
# ==========================================

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'tier', 'total_points',
            'lifetime_points', 'phone_number', 'is_verified',
            'use_codename', 'codename'
        ]
        read_only_fields = ['tier', 'total_points', 'lifetime_points', 'is_verified']


class RewardLedgerSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    related_report_id = serializers.UUIDField(
        source='related_report.id',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = RewardLedger
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'points', 'description', 'related_report_id', 'created_at'
        ]


class RewardCatalogSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = RewardCatalog
        fields = [
            'id', 'title', 'description', 'category',
            'points_required', 'min_tier_required',
            'quantity_available', 'is_available'
        ]


class RedemptionSerializer(serializers.ModelSerializer):
    reward_title = serializers.CharField(source='reward.title', read_only=True)
    reward_category = serializers.CharField(source='reward.category', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Redemption
        fields = [
            'id', 'reward', 'reward_title', 'reward_category',
            'points_deducted', 'status', 'status_display',
            'delivery_details', 'admin_review_notes',
            'created_at', 'reviewed_at', 'fulfilled_at'
        ]
        read_only_fields = [
            'points_deducted', 'status', 'admin_review_notes',
            'reviewed_at', 'fulfilled_at'
        ]


class RedeemRewardSerializer(serializers.Serializer):
    reward_id = serializers.IntegerField()
    delivery_details = serializers.CharField(required=False, allow_blank=True)


class MyReportSerializer(serializers.ModelSerializer):
    lga_name = serializers.CharField(source='lga.name', read_only=True, default='Unknown')

    class Meta:
        model = Report
        fields = [
            'id', 'submitted_at', 'lga_name', 'issue_category',
            'intel_quality_score', 'points_awarded', 'status',
            'ai_urgency_level', 'ai_confidence_score'
        ]


class DashboardLedgerSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = RewardLedger
        fields = ['id', 'transaction_type_display', 'points', 'description', 'created_at']

class DashboardRedemptionSerializer(serializers.ModelSerializer):
    reward_title = serializers.CharField(source='reward.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Redemption
        fields = ['id', 'reward_title', 'points_deducted', 'status_display', 'created_at']

class DashboardRewardSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = RewardCatalog
        fields = ['id', 'title', 'description', 'category', 'points_required', 'is_available']

class RewardsDashboardSerializer(serializers.Serializer):
    """Strict contract for the dashboard payload"""
    profile = serializers.DictField()
    recent_transactions = DashboardLedgerSerializer(many=True)
    active_redemptions = DashboardRedemptionSerializer(many=True)
    affordable_rewards = DashboardRewardSerializer(many=True)
    next_tier = serializers.CharField(allow_null=True)
    points_to_next_tier = serializers.IntegerField(allow_null=True)


# Add this at the bottom of the file:
class RedeemRewardSerializer(serializers.Serializer):
    reward_id = serializers.IntegerField()

    def validate_reward_id(self, value):
        try:
            return RewardCatalog.objects.get(id=value, is_available=True)
        except RewardCatalog.DoesNotExist:
            raise serializers.ValidationError("Reward not found or unavailable.")