from django.contrib import admin, messages
from django.utils import timezone
from .models import Report, FieldVerification, UserProfile, RewardCatalog, RewardLedger, IntelligenceSummary
from .services.intelligence_cycle import IntelligenceCycleEngine

# ✅ CUSTOM ADMIN ACTION FOR ONE-CLICK SITREP
@admin.action(description='🚨 Generate and Email Daily SITREP Now')
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

# ✅ REPORT ADMIN (With the new action attached)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_by', 'issue_category', 'ai_urgency_level', 'status', 'submitted_at')
    list_filter = ('status', 'ai_urgency_level', 'issue_category')
    search_fields = ('description', 'submitted_by__username')
    actions = [generate_and_email_sitrep] # ✅ Action is here!

# ✅ FIELD VERIFICATION ADMIN
@admin.register(FieldVerification)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'assigned_agent', 'status', 'created_at')
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

# ✅ INTELLIGENCE SUMMARY ADMIN (REGISTERED ONLY ONCE!)
@admin.register(IntelligenceSummary)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'summary_type', 'generated_at')
    list_filter = ('summary_type',)
    # We don't need the action here since it's on the Report admin, 
    # but you can add it to actions = [generate_and_email_sitrep] if you prefer.
