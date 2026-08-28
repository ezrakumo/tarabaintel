import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name

class LGA(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, related_name='lgas', on_delete=models.CASCADE)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name

class Ward(models.Model):
    name = models.CharField(max_length=100)
    lga = models.ForeignKey(LGA, related_name='wards', on_delete=models.CASCADE)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name

class PollingUnit(models.Model):
    name = models.CharField(max_length=100)
    ward = models.ForeignKey(Ward, related_name='polling_units', on_delete=models.CASCADE)
    location = gis_models.PointField(srid=4326, null=True, blank=True)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = gis_models.PointField(srid=4326, null=True, blank=True)
    lga = models.ForeignKey(LGA, related_name='reports', on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    issue_category = models.CharField(max_length=50, choices=[
        ('WATER', 'Water'), ('HEALTH', 'Health'), ('AGRIC', 'Agriculture'),
        ('SECURITY', 'Security'), ('INFRA', 'Infrastructure'), ('EDUCATION', 'Education'), ('OTHER', 'Other')
    ])
    status = models.CharField(max_length=20, choices=[
        ('RAW', 'Raw Observation'), ('PENDING_VERIFICATION', 'Pending Verification'),
        ('VERIFIED', 'Verified Intelligence'), ('DISCARDED', 'Discarded')
    ], default='RAW')
    submitted_at = models.DateTimeField(default=timezone.now)
    evidence_set = models.JSONField(default=list, blank=True)

    # --- AI Analytics Fields ---
    ai_suggested_category = models.CharField(max_length=50, blank=True, null=True)
    ai_confidence_score = models.FloatField(default=0.0)
    
    # THESE ARE THE MISSING FIELDS:
    ai_sentiment = models.CharField(max_length=20, blank=True, null=True)
    ai_urgency_level = models.CharField(max_length=20, blank=True, null=True)
    ai_extracted_entities = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"Report {self.id} - {self.issue_category}"

class FieldAgent(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    agent_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20)
    assigned_lgas = models.ManyToManyField(LGA, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.agent_id

class FieldVerification(models.Model):
    report = models.OneToOneField(Report, related_name='verification', on_delete=models.CASCADE)
    assigned_agent = models.ForeignKey(FieldAgent, related_name='verifications', on_delete=models.SET_NULL, null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)
    verification_photos = models.JSONField(default=list, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(default=timezone.now)
    claimed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending Assignment'), ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')
    ], default='PENDING')

    def complete_verification(self, is_valid, notes):
        self.is_verified = is_valid
        self.verification_notes = notes
        self.completed_at = timezone.now()
        self.status = 'COMPLETED'
        self.verified_at = timezone.now()
        self.save()

        self.report.status = 'VERIFIED' if is_valid else 'DISCARDED'
        self.report.save()
        return self.report

    def __str__(self):
        return f"Verification for {self.report.id}"