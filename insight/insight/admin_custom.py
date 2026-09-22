from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from .models import (
    Report, FieldAgent, FieldVerification, LGA, 
    IntelligenceSummary, PatternAlert, RewardCatalog, 
    RewardLedger, UserProfile, AgentRegistrationRequest, Redemption
)

class TarabaInsightAdminSite(AdminSite):
    site_header = "TarabaInsight Command Center"
    site_title = "TarabaInsight Admin"
    index_title = "Intelligence Operations Dashboard"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('command-dashboard/', self.admin_view(self.command_dashboard), name='command_dashboard'),
        ]
        return custom_urls + urls
    
    def command_dashboard(self, request):
        context = {
            'total_reports': Report.objects.count(),
            'critical_reports': Report.objects.filter(ai_urgency_level='CRITICAL').count(),
            'pending_verifications': FieldVerification.objects.filter(status='PENDING').count(),
            'active_agents': FieldAgent.objects.filter(is_active=True).count(),
            'total_agents': UserProfile.objects.filter(tier='AGENT').count(),
            'pending_registrations': AgentRegistrationRequest.objects.filter(status='PENDING').count(),
        }
        return render(request, 'admin/command_dashboard.html', context)

# Initialize custom admin site
admin_site = TarabaInsightAdminSite(name='tarabaintel_admin')

# Register models with enhanced configurations
@admin.register(Report, site=admin_site)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_by', 'issue_category', 'urgency_badge', 'status_badge', 'submitted_at', 'lga_name')
    list_filter = ('status', 'ai_urgency_level', 'issue_category', 'submitted_at')
    search_fields = ('description', 'submitted_by__username', 'issue_category')
    readonly_fields = ('submitted_at', 'updated_at', 'ai_summary')
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Report Details', {
            'fields': ('submitted_by', 'lga', 'issue_category', 'description', 'status')
        }),
        ('Location Data', {
            'fields': ('location', 'lat', 'lon'),
            'classes': ('collapse',)
        }),
        ('AI Analysis', {
            'fields': ('ai_urgency_level', 'ai_confidence_score', 'ai_summary', 'auto_flagged_critical'),
            'classes': ('collapse',)
        }),
        ('Media & Tracking', {
            'fields': ('image_base64', 'is_covert', 'intel_quality_score', 'points_awarded'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def urgency_badge(self, obj):
        colors = {
            'LOW': '#28a745',
            'MODERATE': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
        color = colors.get(obj.ai_urgency_level, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.ai_urgency_level
        )
    urgency_badge.short_description = 'Urgency'
    
    def status_badge(self, obj):
        colors = {
            'RAW': '#6c757d',
            'PROCESSED': '#17a2b8',
            'VERIFIED': '#28a745',
            'REJECTED': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    def lga_name(self, obj):
        return obj.lga.name if obj.lga else 'Unknown'
    lga_name.short_description = 'LGA'

@admin.register(FieldAgent, site=admin_site)
class FieldAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'is_active_badge', 'assigned_lga_name')
    list_filter = ('is_active', 'assigned_lga')
    search_fields = ('name', 'agent_id')
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #28a745; font-weight: bold;">● Active</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">● Inactive</span>')
    is_active_badge.short_description = 'Status'
    
    def assigned_lga_name(self, obj):
        return obj.assigned_lga.name if obj.assigned_lga else 'Unassigned'
    assigned_lga_name.short_description = 'Assigned LGA'

@admin.register(FieldVerification, site=admin_site)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_link', 'assigned_agent_name', 'status_badge', 'is_valid_badge', 'assigned_at')
    list_filter = ('status', 'is_valid', 'assigned_at')
    search_fields = ('report__id', 'assigned_agent__name')
    readonly_fields = ('assigned_at', 'claimed_at', 'verified_at')
    
    fieldsets = (
        ('Verification Details', {
            'fields': ('report', 'assigned_agent', 'status')
        }),
        ('Verification Result', {
            'fields': ('is_valid', 'notes'),
        }),
        ('Timestamps', {
            'fields': ('assigned_at', 'claimed_at', 'verified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def report_link(self, obj):
        if obj.report:
            return format_html('<a href="/admin/insight/report/{}/change/">{}</a>', obj.report.id, f"Report #{obj.report.id}")
        return "N/A"
    report_link.short_description = 'Report'
    
    def assigned_agent_name(self, obj):
        return obj.assigned_agent.name if obj.assigned_agent else 'Unassigned'
    assigned_agent_name.short_description = 'Agent'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#6c757d',
            'ASSIGNED': '#17a2b8',
            'IN_PROGRESS': '#ffc107',
            'COMPLETED': '#28a745',
            'FAILED': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    def is_valid_badge(self, obj):
        if obj.is_valid is None:
            return format_html('<span style="color: #6c757d;">Pending</span>')
        if obj.is_valid:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Valid</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Invalid</span>')
    is_valid_badge.short_description = 'Verification'

@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'tier_badge', 'total_points', 'lifetime_points', 'is_verified_badge')
    list_filter = ('tier', 'is_verified')
    search_fields = ('user__username', 'user__first_name', 'codename')
    
    def user_link(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.user.id, obj.user.username)
    user_link.short_description = 'User'
    
    def tier_badge(self, obj):
        colors = {
            'CITIZEN': '#6c757d',
            'VOLUNTEER': '#17a2b8',
            'INFORMANT': '#fd7e14',
            'AGENT': '#28a745'
        }
        color = colors.get(obj.tier, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.tier
        )
    tier_badge.short_description = 'Tier'
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Verified</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Unverified</span>')
    is_verified_badge.short_description = 'Status'

@admin.register(AgentRegistrationRequest, site=admin_site)
class AgentRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'lga', 'status_badge', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('full_name', 'phone_number', 'email')
    readonly_fields = ('submitted_at', 'approved_at', 'approved_by')
    actions = ['bulk_approve_agents', 'bulk_reject_agents']
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('full_name', 'phone_number', 'email', 'lga')
        }),
        ('Application Details', {
            'fields': ('reason_for_joining', 'status')
        }),
        ('Admin Review', {
            'fields': ('approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',
            'APPROVED': '#28a745',
            'REJECTED': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    @admin.action(description='✅ Approve Selected Agents')
    def bulk_approve_agents(self, request, queryset):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        count = 0
        for registration in queryset.filter(status='PENDING'):
            try:
                user = User.objects.create_user(
                    username=registration.phone_number,
                    password=registration.phone_number,
                    first_name=registration.full_name,
                    email=registration.email or '',
                )
                UserProfile.objects.create(
                    user=user, tier='CITIZEN', total_points=0, lifetime_points=0,
                    phone_number=registration.phone_number,
                )
                agent_count = FieldAgent.objects.count()
                agent_id = f"AGENT_{agent_count + 1:03d}"
                FieldAgent.objects.create(
                    agent_id=agent_id, name=registration.full_name, is_active=True
                )
                registration.status = 'APPROVED'
                registration.approved_by = request.user
                registration.approved_at = timezone.now()
                registration.save()
                count += 1
            except Exception as e:
                print(f"❌ Error approving {registration.phone_number}: {str(e)}")
        self.message_user(request, f'{count} agent(s) approved successfully!', level=admin.messages.SUCCESS)
    
    @admin.action(description='❌ Reject Selected Agents')
    def bulk_reject_agents(self, request, queryset):
        count = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f'{count} agent(s) rejected.', level=admin.messages.SUCCESS)

@admin.register(RewardCatalog, site=admin_site)
class RewardCatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points_required', 'min_tier_required', 'is_available_badge')
    list_filter = ('is_active', 'category', 'min_tier_required')
    search_fields = ('title', 'description')

    def is_available_badge(self, obj):
        if obj.is_available:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Available</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Unavailable</span>')
    is_available_badge.short_description = 'Status'

@admin.register(RewardLedger, site=admin_site)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = ('user_profile_link', 'transaction_type', 'points_badge', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user_profile__user__username', 'description')
    readonly_fields = ('created_at',)
    
    def user_profile_link(self, obj):
        return format_html('<a href="/admin/insight/userprofile/{}/change/">{}</a>', obj.user_profile.id, obj.user_profile.user.username)
    user_profile_link.short_description = 'User'
    
    def points_badge(self, obj):
        color = '#28a745' if obj.points > 0 else '#dc3545'
        return format_html('<span style="color: {}; font-weight: bold;">{:+d}</span>', color, obj.points)
    points_badge.short_description = 'Points'

@admin.register(IntelligenceSummary, site=admin_site)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'generated_at', 'report_count')
    readonly_fields = ('generated_at', 'statistics', 'key_findings', 'emerging_threats', 'recommendations')

@admin.register(PatternAlert, site=admin_site)
class PatternAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity_badge', 'alert_type', 'detected_at', 'acknowledged_badge')
    list_filter = ('severity', 'acknowledged', 'detected_at')
    
    def severity_badge(self, obj):
        colors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107',
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.severity
        )
    severity_badge.short_description = 'Severity'
    
    def acknowledged_badge(self, obj):
        if obj.acknowledged:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Acknowledged</span>')
        return format_html('<span style="color: #dc3545; font-weight: bold;">✗ Pending</span>')
    acknowledged_badge.short_description = 'Status'

@admin.register(LGA, site=admin_site)
class LGAAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'population')
    search_fields = ('name', 'state')