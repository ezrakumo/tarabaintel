from django.contrib import admin
from django.utils import timezone
from .models import (
    Report, FieldAgent, FieldVerification, LGA,
    IntelligenceSummary, PatternAlert,
    UserProfile, RewardLedger, RewardCatalog, Redemption
)


# ==========================================
# CORE INTELLIGENCE ADMIN
# ==========================================

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'submitted_at', 'issue_category', 'ai_urgency_level', 'ai_confidence_score', 'intel_quality_score', 'points_awarded', 'status')
    list_filter = ('status', 'ai_urgency_level', 'issue_category')
    search_fields = ('description', 'id')
    readonly_fields = ('id', 'submitted_at')


@admin.register(FieldAgent)
class FieldAgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'name', 'is_active', 'assigned_lga')
    list_filter = ('is_active',)
    search_fields = ('agent_id', 'name')


@admin.register(FieldVerification)
class FieldVerificationAdmin(admin.ModelAdmin):
    list_display = ('report', 'assigned_agent', 'status', 'assigned_at', 'verified_at')
    list_filter = ('status',)
    search_fields = ('report__id', 'assigned_agent__agent_id')


@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'population')
    search_fields = ('name', 'state')


@admin.register(IntelligenceSummary)
class IntelligenceSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'generated_at', 'report_count')
    list_filter = ('generated_at',)
    search_fields = ('title', 'executive_briefing')
    readonly_fields = ('generated_at',)


@admin.register(PatternAlert)
class PatternAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'severity', 'detected_at', 'acknowledged')
    list_filter = ('severity', 'alert_type', 'acknowledged')
    search_fields = ('title', 'description')


# ==========================================
# TARABAINSIGHT 2.0: REWARD ADMIN
# ==========================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'total_points', 'lifetime_points', 'is_verified', 'phone_number')
    list_filter = ('tier', 'is_verified')
    search_fields = ('user__username', 'phone_number', 'codename')
    readonly_fields = ('total_points', 'lifetime_points')


@admin.register(RewardLedger)
class RewardLedgerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'transaction_type', 'points', 'related_report', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user_profile__user__username', 'description')
    readonly_fields = ('created_at', 'user_profile', 'transaction_type', 'points', 'description', 'related_report')


@admin.register(RewardCatalog)
class RewardCatalogAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points_required', 'min_tier_required', 'quantity_available', 'is_active')
    list_filter = ('category', 'is_active', 'min_tier_required')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'quantity_available')


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'reward', 'points_deducted', 'status', 'created_at', 'fulfilled_at')
    list_filter = ('status', 'reward__category', 'created_at')
    search_fields = ('user_profile__user__username', 'reward__title')
    readonly_fields = ('created_at', 'reviewed_at', 'fulfilled_at', 'user_profile', 'reward', 'points_deducted')
    actions = ['approve_redemptions', 'reject_redemptions', 'mark_fulfilled', 'export_payout_csv']

    def approve_redemptions(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='PENDING').update(
            status='APPROVED', 
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'✅ {updated} redemption(s) approved for payout.')
    approve_redemptions.short_description = "✅ Approve Selected for Payout"

    def reject_redemptions(self, request, queryset):
        from django.utils import timezone
        count = 0
        for r in queryset.filter(status='PENDING'):
            r.status = 'REJECTED'
            r.reviewed_by = request.user
            r.reviewed_at = timezone.now()
            r.save()
            # Refund points
            r.user_profile.total_points += r.points_deducted
            r.user_profile.save()
            RewardLedger.objects.create(
                user_profile=r.user_profile,
                transaction_type='ADMIN_ADJUSTMENT',
                points=r.points_deducted,
                description=f'Refund for rejected redemption: {r.reward.title}',
            )
            count += 1
        self.message_user(request, f'❌ {count} redemption(s) rejected and points refunded.')
    reject_redemptions.short_description = "❌ Reject & Refund Points"

    def mark_fulfilled(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='APPROVED').update(
            status='FULFILLED',
            fulfilled_at=timezone.now()
        )
        self.message_user(request, f'🎁 {updated} redemption(s) marked as fulfilled/paid.')
    mark_fulfilled.short_description = "🎁 Mark as Fulfilled (Paid Out)"

    def export_payout_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payouts_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['User', 'Phone', 'Reward', 'Points', 'Delivery Details', 'Status'])
        for r in queryset:
            writer.writerow([
                r.user_profile.user.username,
                r.user_profile.phone_number or 'N/A',
                r.reward.title,
                r.points_deducted,
                r.delivery_details,
                r.status
            ])
        return response
    export_payout_csv.short_description = "📥 Export Selected to CSV for Payout"