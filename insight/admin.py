from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from .models import State, LGA, Ward, PollingUnit, Report,FieldAgent, FieldVerification
from .models import Report, FieldAgent, FieldVerification, LGA, IntelligenceSummary, PatternAlert, UserProfile, RewardLedger

# ==========================================
# Geographic Models (With Interactive Map Views)
# ==========================================

@admin.register(State)
class StateAdmin(gis_admin.GISModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(LGA)
class LGAAdmin(gis_admin.GISModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state',)
    search_fields = ('name',)

@admin.register(Ward)
class WardAdmin(gis_admin.GISModelAdmin):
    list_display = ('name', 'lga')
    list_filter = ('lga__state', 'lga')
    search_fields = ('name',)

@admin.register(PollingUnit)
class PollingUnitAdmin(gis_admin.GISModelAdmin):
    list_display = ('name', 'ward')
    list_filter = ('ward__lga__state', 'ward__lga')
    search_fields = ('name',)

# ==========================================
# Core Operations Models
# ==========================================

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue_category', 'status', 'lga', 'submitted_at')
    list_filter = ('status', 'issue_category', 'lga')
    search_fields = ('description', 'id')
    readonly_fields = ('id', 'submitted_at')

#@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'media_type', 'uploaded_at')
    list_filter = ('media_type',)

@admin.register(FieldAgent)
class FieldAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'user', 'phone_number', 'is_active')
    list_filter = ('is_active', 'assigned_lgas')
    search_fields = ('agent_id', 'user__username')

@admin.register(FieldVerification)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('report', 'assigned_agent', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status', 'is_verified')
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'total_points', 'is_verified', 'phone_number')
    list_filter = ('tier', 'is_verified')
    search_fields = ('user__username', 'phone_number', 'codename')

@admin.register(RewardLedger)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'points', 'transaction_type', 'related_report', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user_profile__user__username', 'description')
    readonly_fields = ('created_at',)