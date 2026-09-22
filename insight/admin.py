from django.contrib import admin
from .models import (
    Report, FieldAgent, FieldVerification, LGA, 
    IntelligenceSummary, PatternAlert, RewardCatalog, 
    RewardLedger, UserProfile, AgentRegistrationRequest, Redemption
)

# ✅ SIMPLE, DEFAULT ADMIN REGISTRATION
admin.site.register(Report)
admin.site.register(FieldAgent)
admin.site.register(FieldVerification)
admin.site.register(LGA)
admin.site.register(IntelligenceSummary)
admin.site.register(PatternAlert)
admin.site.register(RewardCatalog)
admin.site.register(RewardLedger)
admin.site.register(UserProfile)
admin.site.register(AgentRegistrationRequest)
admin.site.register(Redemption)