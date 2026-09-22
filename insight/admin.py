from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.apps import apps
from .models import (
    Report, FieldAgent, FieldVerification, LGA, 
    IntelligenceSummary, PatternAlert, RewardCatalog, 
    RewardLedger, UserProfile, AgentRegistrationRequest, Redemption
)
from django.utils import timezone

# ✅ CUSTOM ADMIN SITE WITH BRANDING
class TarabaInsightAdminSite(AdminSite):
    site_header = "TarabaInsight Command Center"
    site_title = "TarabaInsight Intelligence Operations"
    index_title = "Dashboard"
    
admin_site = TarabaInsightAdminSite(name='tarabaintel')

# ✅ REGISTER ALL MODELS WITH ENHANCED CONFIGURATIONS

@admin.register(Report, site=admin_site)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_by', 'issue_category', 'urgency_badge', 'status_badge', 'submitted_at')
    list_filter = ('status', 'ai_urgency_level', 'issue_category')
    search_fields = ('description', 'submitted_by__username')
    readonly_fields = ('submitted_at', 'updated_at')
    
    def urgency_badge(self, obj):
        colors = {'LOW': '#28a745', 'MODERATE': '#ffc107', 'HIGH': '#fd7e14', 'CRITICAL': '#dc3545'}
        color = colors.get(obj.ai_urgency_level, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:3px 10px;border-radius:3px;font-weight:bold;">{}</span>', color, obj.ai_urgency_level)
    urgency_badge.short_description = 'Urgency'
    
    def status_badge(self, obj):
        colors = {'RAW': '#6c757d', 'PROCESSED': '#17a2b8', 'VERIFIED': '#28a745', 'REJECTED': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:3px 10px;border-radius:3px;font-weight:bold;">{}</span>', color, obj.status)
    status_badge.short_description = 'Status'

@admin.register(FieldAgent, site=admin_site)
class FieldAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'is_active_badge', 'assigned_lga')
    list_filter = ('is_active',)
    search_fields = ('name', 'agent_id')
    
    def is_active_badge(self, obj):
        return format_html('<span style="color:{};font-weight:bold;">● {}</span>', '#28a745' if obj.is_active else '#dc3545', 'Active' if obj.is_active else 'Inactive')
    is_active_badge.short_description = 'Status'

@admin.register(FieldVerification, site=admin_site)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'assigned_agent', 'status_badge', 'assigned_at')
    list_filter = ('status', 'is_valid')
    search_fields = ('report__id', 'assigned_agent__name')
    readonly_fields = ('assigned_at', 'claimed_at', 'verified_at')
    
    def status_badge(self, obj):
        colors = {'PENDING': '#6c757d', 'ASSIGNED': '#17a2b8', 'IN_PROGRESS': '#ffc107', 'COMPLETED': '#28a745', 'FAILED': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:3px 10px;border-radius:3px;font-weight:bold;">{}</span>', color, obj.status)
    status_badge.short_description = 'Status'

@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier_badge', 'total_points', 'lifetime_points')
    list_filter = ('tier', 'is_verified')
    search_fields = ('user__username', 'codename')
    
    def tier_badge(self, obj):
        colors = {'CITIZEN': '#6c757d', 'VOLUNTEER': '#17a2b8', 'INFORMANT': '#fd7e14', 'AGENT': '#28a745'}
        color = colors.get(obj.tier, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:3px 10px;border-radius:3px;font-weight:bold;">{}</span>', color, obj.tier)
    tier_badge.short_description = 'Tier'

@admin.register(AgentRegistrationRequest, site=admin_site)
class AgentRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'status_badge', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('full_name', 'phone_number')
    readonly_fields = ('submitted_at', 'approved_at', 'approved_by')
    actions = ['bulk_approve_agents', 'bulk_reject_agents']
    
    def status_badge(self, obj):
        colors = {'PENDING': '#ffc107', 'APPROVED': '#28a745', 'REJECTED': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="color:white;background:{};padding:3px 10px;border-radius:3px;font-weight:bold;">{}</span>', color, obj.status)
    status_badge.short_description = 'Status'
    
    @admin.action(description='✅ Approve Selected Agents')
    def bulk_approve_agents(self, request, queryset):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        count = 0
        for reg in queryset.filter(status='PENDING'):
            try:
                user = User.objects.create_user(username=reg.phone_number, password=reg.phone_number, first_name=reg.full_name, email=reg.email or '')
                UserProfile.objects.create(user=user, tier='CITIZEN', total_points=0, lifetime_points=0, phone_number=reg.phone_number)
                agent_count = FieldAgent.objects.count()
                agent_id = f"AGENT_{agent_count + 1:03d}"
                FieldAgent.objects.create(agent_id=agent_id, name=reg.full_name, is_active=True)
                reg.status = 'APPROVED'
                reg.approved_by = request.user
                reg.approved_at = timezone.now()
                reg.save()
                count += 1
            except Exception as e:
                print(f"❌ Error: {e}")
        self.message_user(request, f'{count} agent(s) approved!', level=admin.messages.SUCCESS)
    
    @admin.action(description=' Reject Selected Agents')
    def bulk_reject_agents(self, request, queryset):
        count = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f'{count} agent(s) rejected.')

@admin.register(RewardCatalog, site=admin_site)
class RewardCatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required', 'min_tier_required', 'is_active')
    list_filter = ('is_active', 'category')

@admin.register(RewardLedger, site=admin_site)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'transaction_type', 'points', 'created_at')
    list_filter = ('transaction_type',)

@admin.register(IntelligenceSummary, site=admin_site)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'generated_at', 'report_count')

@admin.register(PatternAlert, site=admin_site)
class PatternAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'alert_type', 'acknowledged')
    list_filter = ('severity', 'acknowledged')

@admin.register(LGA, site=admin_site)
class LGAAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'population')

# ✅ REGISTER DEFAULT ADMIN TOO (for Users/Groups)
admin.site.register(apps.get_model('auth', 'Group'))