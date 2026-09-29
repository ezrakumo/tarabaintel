from django.contrib import admin
from django.utils import timezone
from .models import (
    LGA, Report, FieldAgent, FieldVerification, 
    IntelligenceSummary, PatternAlert, 
    UserProfile, RewardLedger, RewardCatalog, Redemption,
    AgentRegistrationRequest
)

# ✅ 1. LGA ADMIN
@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'population')
    list_filter = ('state',)
    search_fields = ('name',)

# ✅ 2. REPORT ADMIN (The Core Intelligence)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue_category', 'get_urgency', 'lga', 'state', 'status', 'submitted_at')
    list_filter = ('state', 'ai_urgency_level', 'issue_category', 'status', 'lga')
    search_fields = ('description', 'lga__name', 'submitted_by__username')
    readonly_fields = ('submitted_at', 'ai_suggested_category', 'ai_confidence_score', 'ai_sentiment', 'ai_urgency_level', 'ai_extracted_entities', 'intel_quality_score', 'points_awarded')
    ordering = ('-submitted_at',)
    
    def get_urgency(self, obj):
        if obj.ai_urgency_level == 'CRITICAL':
            return f'🔴 {obj.ai_urgency_level}'
        elif obj.ai_urgency_level == 'HIGH':
            return f'🟠 {obj.ai_urgency_level}'
        return obj.ai_urgency_level
    get_urgency.short_description = 'Urgency'

# ✅ 3. FIELD AGENT ADMIN
@admin.register(FieldAgent)
class FieldAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'assigned_lga', 'is_active')
    list_filter = ('is_active', 'assigned_lga')
    search_fields = ('name', 'agent_id')

# ✅ 4. FIELD VERIFICATION ADMIN
@admin.register(FieldVerification)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'assigned_agent', 'status', 'is_valid', 'assigned_at')
    list_filter = ('status', 'is_valid')
    search_fields = ('report__description', 'assigned_agent__name')

# ✅ 5. INTELLIGENCE SUMMARY ADMIN (AI SITREPS)
@admin.register(IntelligenceSummary)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'generated_at')
    readonly_fields = ('title', 'content', 'generated_at', 'statistics')
    ordering = ('-generated_at',)

# ✅ 6. PATTERN ALERT ADMIN
@admin.register(PatternAlert)
class PatternAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'alert_type', 'detected_at', 'acknowledged')
    list_filter = ('severity', 'acknowledged', 'alert_type')
    search_fields = ('title', 'description')
    ordering = ('-detected_at',)

# ✅ 7. USER PROFILE ADMIN
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'tier', 'total_points', 'lifetime_points', 'is_verified')
    list_filter = ('state', 'tier', 'is_verified')
    search_fields = ('user__username', 'user__first_name', 'phone_number', 'codename')

# ✅ 8. REWARD CATALOG ADMIN
@admin.register(RewardCatalog)
class RewardCatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points_required', 'min_tier_required', 'is_active')
    list_filter = ('category', 'min_tier_required', 'is_active')
    search_fields = ('title', 'description')

# ✅ 9. REWARD LEDGER ADMIN
@admin.register(RewardLedger)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'transaction_type', 'points', 'created_at')
    list_filter = ('transaction_type',)
    search_fields = ('user_profile__user__username', 'description')
    readonly_fields = ('created_at',)

# ✅ 10. REDEMPTION ADMIN
@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'reward', 'points_deducted', 'status', 'created_at')
    list_filter = ('status', 'reward__category')
    search_fields = ('user_profile__user__username', 'delivery_details')
    readonly_fields = ('created_at', 'reviewed_at', 'fulfilled_at')

# ✅ 11. AGENT REGISTRATION REQUEST ADMIN (CRITICAL FOR ONBOARDING)
@admin.register(AgentRegistrationRequest)
class AgentRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'lga', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('full_name', 'phone_number', 'email', 'lga')
    readonly_fields = ('submitted_at', 'approved_by', 'approved_at', 'rejection_reason')
    
    actions = ['approve_agents', 'reject_agents']

    @admin.action(description='Approve selected agents')
    def approve_agents(self, request, queryset):
        count = 0
        for obj in queryset.filter(status='PENDING'):
            obj.status = 'APPROVED'
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
            obj.save()
            count += 1
        self.message_user(request, f'{count} agents approved successfully.')

    @admin.action(description='Reject selected agents')
    def reject_agents(self, request, queryset):
        count = 0
        for obj in queryset.filter(status='PENDING'):
            obj.status = 'REJECTED'
            obj.save()
            count += 1
        self.message_user(request, f'{count} agents rejected.')