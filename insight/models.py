import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.utils import timezone  # ✅ ADDED MISSING TIMEZONE IMPORT

# ==========================================
# CORE INTELLIGENCE MODELS
# ==========================================

class LGA(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Taraba')
    population = models.IntegerField(default=0)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name


# ✅ 1. ADDED THE MISSING REPORT MODEL (MUST BE ABOVE FIELDVERIFICATION)
class Report(models.Model):
    STATUS_CHOICES = [
        ('RAW', 'Raw Submission'),
        ('PROCESSED', 'AI Processed'),
        ('VERIFIED', 'Field Verified'),
        ('REJECTED', 'Rejected'),
    ]
    URGENCY_CHOICES = [
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True)
    issue_category = models.CharField(max_length=100)
    description = models.TextField()
    
    # Location data
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    
    # AI Analysis
    ai_urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='MODERATE')
    ai_confidence_score = models.FloatField(default=0.5)
    ai_summary = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RAW')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Report #{self.id} - {self.issue_category} ({self.status})"


class FieldAgent(models.Model):
    agent_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    assigned_lga = models.ForeignKey(LGA, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.agent_id})"


class FieldVerification(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    # ✅ NOW 'Report' IS DEFINED ABOVE, SO THIS WORKS PERFECTLY
    report = models.OneToOneField(Report, on_delete=models.CASCADE, related_name='verification')
    assigned_agent = models.ForeignKey(FieldAgent, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    assigned_at = models.DateTimeField(auto_now_add=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_valid = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f"Verification for Report {self.report.id}"

    def complete_verification(self, is_valid, notes=''):
        self.is_valid = is_valid
        self.notes = notes
        self.verified_at = timezone.now()
        self.status = 'COMPLETED' if is_valid else 'FAILED'
        self.save()
        self.report.status = 'VERIFIED' if is_valid else 'REJECTED'
        self.report.save()


class IntelligenceSummary(models.Model):
    title = models.CharField(max_length=200)
    executive_briefing = models.TextField()
    key_findings = models.JSONField(default=list)
    emerging_threats = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    statistics = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return self.title


class PatternAlert(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    alert_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    detected_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    
    # ✅ NOW 'Report' IS DEFINED ABOVE, SO THIS WORKS PERFECTLY
    related_reports = models.ManyToManyField(Report, blank=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.title} ({self.severity})"


# ==========================================
# TARABAINSIGHT 2.0: HUMINT & REWARD SYSTEM
# ==========================================

USER_TIERS = [
    ('CITIZEN', 'Citizen'),
    ('VOLUNTEER', 'Vetted Volunteer'),
    ('INFORMANT', 'Covert Informant'),
    ('AGENT', 'Official Field Agent'),
]

TRANSACTION_TYPES = [
    ('EARNED_SUBMISSION', 'Points Earned: Report Submitted'),
    ('EARNED_ACTIONABLE', 'Points Earned: Intel Graded Actionable'),
    ('EARNED_VERIFIED', 'Points Earned: Intel Physically Verified'),
    ('REDEEMED_AIRTIME', 'Points Redeemed: Airtime/Data'),
    ('REDEEMED_MATERIAL', 'Points Redeemed: Physical Materials'),
    ('REDEEMED_SCHOLARSHIP', 'Points Redeemed: Scholarship/Education'),
    ('REDEEMED_CASH', 'Points Redeemed: Cash Reward'),
    ('REDEEMED_BADGE', 'Points Redeemed: Digital Badge'),
    ('ADMIN_ADJUSTMENT', 'Admin Manual Adjustment'),
]

REWARD_CATEGORIES = [
    ('AIRTIME', 'Airtime / Data Bundle'),
    ('MATERIAL', 'Physical Materials'),
    ('SCHOLARSHIP', 'Scholarship / Education'),
    ('CASH', 'Cash Reward'),
    ('BADGE', 'Digital Badge / Award'),
]

REDEMPTION_STATUS = [
    ('PENDING', 'Pending Approval'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('FULFILLED', 'Fulfilled'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='intel_profile')
    tier = models.CharField(max_length=20, choices=USER_TIERS, default='CITIZEN')
    total_points = models.IntegerField(default=0, help_text="Current available reward points")
    lifetime_points = models.IntegerField(default=0, help_text="Total points earned historically")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="For SMS acknowledgments and rewards")
    is_verified = models.BooleanField(default=False, help_text="Has an admin vetted this user?")
    use_codename = models.BooleanField(default=False)
    codename = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "User Profiles & Tiers"

    def __str__(self):
        name = self.codename if self.use_codename and self.codename else self.user.username
        return f"{name} ({self.get_tier_display()}) - {self.total_points} pts"


class RewardLedger(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='ledger_entries')
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    points = models.IntegerField(help_text="Positive for earned, negative for redeemed")
    description = models.TextField(blank=True, help_text="Reason for transaction")
    related_report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Reward Ledger"

    def __str__(self):
        return f"{self.user_profile} | {self.points} pts | {self.get_transaction_type_display()}"


class RewardCatalog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=REWARD_CATEGORIES)
    points_required = models.IntegerField(help_text="Points needed to redeem")
    min_tier_required = models.CharField(max_length=20, choices=USER_TIERS, default='CITIZEN', help_text="Minimum user tier to redeem")
    quantity_available = models.IntegerField(default=-1, help_text="-1 means unlimited")
    is_active = models.BooleanField(default=True)
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['points_required']
        verbose_name_plural = "Reward Catalog"

    def __str__(self):
        return f"{self.title} ({self.points_required} pts)"

    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.quantity_available == -1:
            return True
        return self.quantity_available > 0


class Redemption(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(RewardCatalog, on_delete=models.PROTECT, related_name='redemptions')
    points_deducted = models.IntegerField()
    status = models.CharField(max_length=20, choices=REDEMPTION_STATUS, default='PENDING')
    delivery_details = models.TextField(blank=True, help_text="Phone number, address, bank details, etc.")
    admin_review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_redemptions')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_profile} redeemed {self.reward} ({self.status})"


# ✅ 2. CLEAN, SINGLE DEFINITION OF AGENT REGISTRATION (AT THE BOTTOM)
class AgentRegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    lga = models.CharField(max_length=100, blank=True, null=True)
    reason_for_joining = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.phone_number} ({self.status})"
