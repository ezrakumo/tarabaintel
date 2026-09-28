from django.contrib import admin
from .models import Report, FieldVerification, IntelligenceSummary, UserProfile

# ✅ 1. REPORT ADMIN (The Core Intelligence)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue_category', 'ai_urgency_level', 'lga', 'status', 'submitted_at')
    list_filter = ('ai_urgency_level', 'issue_category', 'status', 'lga')
    search_fields = ('description', 'lga__name', 'submitted_by__username')
    readonly_fields = ('submitted_at', 'ai_suggested_category', 'ai_confidence_score', 'ai_sentiment', 'ai_urgency_level')
    ordering = ('-submitted_at',)
    
    # Color-code the urgency levels in the admin list
    def ai_urgency_level(self, obj):
        if obj.ai_urgency_level == 'CRITICAL':
            return f'🔴 {obj.ai_urgency_level}'
        elif obj.ai_urgency_level == 'HIGH':
            return f'🟠 {obj.ai_urgency_level}'
        return obj.ai_urgency_level
    ai_urgency_level.short_description = 'Urgency'

# ✅ 2. FIELD VERIFICATION ADMIN
@admin.register(FieldVerification)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'assigned_agent', 'status', 'is_valid', 'assigned_at')
    list_filter = ('status', 'is_valid')
    search_fields = ('report__description', 'assigned_agent__username')

# ✅ 3. INTELLIGENCE SUMMARY ADMIN (AI SITREPS)
@admin.register(IntelligenceSummary)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'generated_at')
    readonly_fields = ('title', 'content', 'generated_at', 'statistics')
    ordering = ('-generated_at',)

# ✅ 4. USER PROFILE ADMIN
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'total_points', 'lifetime_points')
    list_filter = ('tier',)
    search_fields = ('user__username', 'user__first_name')