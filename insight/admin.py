from django.contrib import admin, messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    FieldAgent, Report, FieldVerification, UserProfile, RewardCatalog, 
    RewardLedger, IntelligenceSummary, AgentRegistrationRequest
)
from .services.intelligence_cycle import IntelligenceCycleEngine

User = get_user_model()

# ✅ CUSTOM ADMIN ACTION FOR ONE-CLICK SITREP
@admin.action(description=' Generate Daily SITREP Now')
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

# ✅ FIELD AGENT ADMIN
@admin.register(FieldAgent)
class FieldAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'is_active', 'assigned_lga')
    list_filter = ('is_active', 'assigned_lga')
    search_fields = ('name', 'agent_id')

# ✅ AGENT REGISTRATION REQUEST ADMIN (WITH FULL APPROVAL LOGIC)
@admin.register(AgentRegistrationRequest)
class AgentRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'lga', 'status', 'submitted_at')
    list_filter = ('status', 'lga', 'submitted_at')
    search_fields = ('full_name', 'phone_number')
    readonly_fields = ('submitted_at', 'approved_at', 'approved_by')
    
    actions = ['bulk_approve_agents', 'bulk_reject_agents']
    
    @admin.action(description='✅ Approve Selected Agents & Create Accounts')
    def bulk_approve_agents(self, request, queryset):
        count = 0
        errors = 0
        
        for registration in queryset.filter(status='PENDING'):
            try:
                # 1. Create Django User account
                user = User.objects.create_user(
                    username=registration.phone_number,
                    password=registration.phone_number,  # Temporary password
                    first_name=registration.full_name,
                    email=registration.email or '',
                    is_active=True, 
                )
                
                # 2. Create UserProfile for rewards system
                UserProfile.objects.create(
                    user=user,
                    tier='CITIZEN',
                    total_points=0,
                    lifetime_points=0,
                    phone_number=registration.phone_number,
                )
                
                # 3. Create FieldAgent record with unique AGENT_ID
                agent_count = FieldAgent.objects.count()
                agent_id = f"AGENT_{agent_count + 1:03d}"  # AGENT_001, AGENT_002, etc.
                
                FieldAgent.objects.create(
                    agent_id=agent_id,
                    name=registration.full_name,
                    is_active=True,
                    assigned_lga=None,  # Can be assigned manually later
                )
                
                # 4. Mark registration as approved
                registration.status = 'APPROVED'
                registration.approved_by = request.user
                registration.approved_at = timezone.now()
                registration.save()
                
                count += 1
                
            except Exception as e:
                errors += 1
                print(f"❌ Error approving {registration.phone_number}: {str(e)}")
        
        if errors > 0:
            self.message_user(request, f'{count} agent(s) approved, {errors} failed. Check logs.', level=messages.WARNING)
        else:
            self.message_user(request, f'{count} agent(s) approved and accounts created! They can login with their phone number.', level=messages.SUCCESS)
    
    @admin.action(description='❌ Reject Selected Agents')
    def bulk_reject_agents(self, request, queryset):
        count = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f'{count} agent(s) rejected.')