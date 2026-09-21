from django.contrib import admin, messages
from django.utils import timezone
from .models import (
    Report, FieldVerification, UserProfile, RewardCatalog, 
    RewardLedger, IntelligenceSummary, AgentRegistrationRequest
)
from .services.intelligence_cycle import IntelligenceCycleEngine

# ✅ CUSTOM ADMIN ACTION FOR ONE-CLICK SITREP
@admin.action(description='🚨 Generate Daily SITREP Now')
def generate_and_email_sitrep(modeladmin, request, queryset):
    try:
        engine = IntelligenceCycleEngine()
        sitrep = engine.generate_daily_sitrep()
        
        modeladmin.message_user(
            request, 
            f"✅ SUCCESS: Daily SITREP generated for {sitrep['date']}. Total Reports: {sitrep['statistics']['total_reports']}. Critical: {sitrep['statistics']['critical_incidents']}", 
            level=messages.SUCCESS
        )
    except Exception as e:
        modeladmin.message_user(
            request, 
            f"❌ ERROR: Failed to generate SITREP. Details: {str(e)}", 
            level=messages.ERROR
        )

# ✅ REPORT ADMIN
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_by', 'issue_category', 'ai_urgency_level', 'status', 'submitted_at')
    list_filter = ('status', 'ai_urgency_level', 'issue_category')
    search_fields = ('description', 'submitted_by__username')
    actions = [generate_and_email_sitrep]

# ✅ FIELD VERIFICATION ADMIN
@admin.register(FieldVerification)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'status', 'is_valid')
    list_filter = ('status', 'is_valid')

# ✅ USER PROFILE ADMIN
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'total_points', 'lifetime_points')
    list_filter = ('tier',)

# ✅ REWARD CATALOG ADMIN
@admin.register(RewardCatalog)
class RewardCatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required', 'min_tier_required', 'is_active')
    list_filter = ('is_active', 'min_tier_required')

# ✅ REWARD LEDGER ADMIN
@admin.register(RewardLedger)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'transaction_type', 'points', 'created_at')
    list_filter = ('transaction_type',)

# ✅ INTELLIGENCE SUMMARY ADMIN
@admin.register(IntelligenceSummary)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'generated_at')

# ✅ NEW: AGENT REGISTRATION REQUEST ADMIN
@admin.register(AgentRegistrationRequest)
class AgentRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'lga', 'status', 'submitted_at')
    list_filter = ('status', 'lga', 'submitted_at')
    search_fields = ('full_name', 'phone_number')
    readonly_fields = ('submitted_at', 'approved_at', 'approved_by')
    
    actions = ['bulk_approve_agents', 'bulk_reject_agents']
    
    @admin.action(description='✅ Approve Selected Agents')
    def bulk_approve_agents(self, request, queryset):
        count = 0
        for registration in queryset.filter(status='PENDING'):
            registration.status = 'APPROVED'
            registration.approved_by = request.user
            registration.approved_at = timezone.now()
            registration.save()
            count += 1
        self.message_user(request, f'{count} agent(s) approved successfully!')
    
    @admin.action(description='❌ Reject Selected Agents')
    def bulk_reject_agents(self, request, queryset):
        count = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f'{count} agent(s) rejected.')