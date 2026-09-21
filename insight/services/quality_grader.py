import re
from django.utils import timezone
from datetime import timedelta
from ..models import Report, UserProfile, RewardLedger

def grade_and_reward_report(report):
    """
    Analyzes a report for quality and awards points to the user's ledger.
    Returns: (quality_score, points_awarded)
    """
    score = 0
    reasons = []

    # 1. COMPLETENESS (Up to 30 pts)
    if report.image_base64:
        score += 15
        reasons.append("Photo evidence attached")
    if report.lga:
        score += 15
        reasons.append("Specific LGA provided")

    # 2. SPECIFICITY (Up to 40 pts)
    description = report.description or ""
    word_count = len(description.split())
    if word_count > 50:
        score += 20
        reasons.append("Detailed description (>50 words)")
    
    if re.search(r'\d+', description):
        score += 20
        reasons.append("Contains specific numbers/dates/coordinates")

    # 3. CORROBORATION (Up to 30 pts)
    if report.lga and report.issue_category:
        week_ago = timezone.now() - timedelta(days=7)
        similar_reports = Report.objects.filter(
            lga=report.lga,
            issue_category=report.issue_category,
            submitted_at__gte=week_ago,
            status__in=['VERIFIED', 'PENDING_VERIFICATION', 'RAW', 'PROCESSED']
        ).exclude(id=report.id).count()
        
        if similar_reports > 0:
            corroboration_pts = min(30, similar_reports * 15)
            score += corroboration_pts
            reasons.append(f"Corroborated by {similar_reports} recent report(s)")

    score = min(100, score)
    report.intel_quality_score = score

    # 4. CALCULATE REWARDS
    points_awarded = 5  # Base acknowledgment points
    ledger_type = 'EARNED_SUBMISSION'
    ledger_desc = f"Base acknowledgment points. Quality Score: {score}/100."

    if score >= 90:
        points_awarded += 145
        ledger_type = 'EARNED_ACTIONABLE'
        ledger_desc = f"HIGH-VALUE INTEL: Quality Score {score}/100. ({', '.join(reasons)})"
    elif score >= 70:
        points_awarded += 45
        ledger_type = 'EARNED_ACTIONABLE'
        ledger_desc = f"Actionable Intel: Quality Score {score}/100. ({', '.join(reasons)})"

    report.points_awarded = points_awarded
    report.acknowledgment_sent = True
    report.status = 'PROCESSED' # ✅ Ensure it moves out of RAW
    report.save()

    # 5. UPDATE USER PROFILE & LEDGER (BULLETPROOF LOOKUP)
    if hasattr(report, 'submitted_by') and report.submitted_by and getattr(report.submitted_by, 'is_authenticated', True):
        try:
            # ✅ Try explicit related_name first, then fallback to Django default
            try:
                profile = report.submitted_by.intel_profile
            except Exception:
                profile = UserProfile.objects.get(user=report.submitted_by)
        except UserProfile.DoesNotExist:
            # Auto-create profile if it doesn't exist
            profile = UserProfile.objects.create(user=report.submitted_by)
        
        # Update points safely
        profile.total_points += points_awarded
        if hasattr(profile, 'lifetime_points'):
            profile.lifetime_points += points_awarded
        profile.save()

        # Create immutable ledger entry
        RewardLedger.objects.create(
            user_profile=profile,
            transaction_type=ledger_type,
            points=points_awarded,
            description=ledger_desc,
            related_report=report
        )
        
        print(f"✅ Reward processed: {report.submitted_by.username} earned {points_awarded} pts (Score: {score})")

    return score, points_awarded
