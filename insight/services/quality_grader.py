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
    
    # Check for numbers/dates (simple heuristic for specific intel)
    if re.search(r'\d+', description):
        score += 20
        reasons.append("Contains specific numbers/dates/coordinates")

    # 3. CORROBORATION (Up to 30 pts)
    # Check if other reports match this LGA and Category in the last 7 days
    if report.lga and report.issue_category:
        week_ago = timezone.now() - timedelta(days=7)
        similar_reports = Report.objects.filter(
            lga=report.lga,
            issue_category=report.issue_category,
            submitted_at__gte=week_ago,
            status__in=['VERIFIED', 'PENDING_VERIFICATION', 'RAW'] # Include recent raw reports
        ).exclude(id=report.id).count()
        
        if similar_reports > 0:
            # 15 pts per corroborating report, max 30 pts
            corroboration_pts = min(30, similar_reports * 15)
            score += corroboration_pts
            reasons.append(f"Corroborated by {similar_reports} recent report(s)")

    # Cap score at 100
    score = min(100, score)

    # Update the Report model
    report.intel_quality_score = score
    report.save()

    # 4. CALCULATE REWARDS
    points_awarded = 5  # Base acknowledgment points for everyone
    ledger_type = 'EARNED_SUBMISSION'
    ledger_desc = f"Base acknowledgment points. Quality Score: {score}/100."

    if score >= 90:
        points_awarded += 145  # Total 150 pts
        ledger_type = 'EARNED_ACTIONABLE'
        ledger_desc = f"HIGH-VALUE INTEL: Quality Score {score}/100. ({', '.join(reasons)})"
    elif score >= 70:
        points_awarded += 45   # Total 50 pts
        ledger_type = 'EARNED_ACTIONABLE'
        ledger_desc = f"Actionable Intel: Quality Score {score}/100. ({', '.join(reasons)})"

    report.points_awarded = points_awarded
    report.acknowledgment_sent = True
    report.save()

    # 5. UPDATE USER PROFILE & LEDGER
    # Check if the report has an associated user (handles anonymous tips gracefully)
    if hasattr(report, 'submitted_by') and report.submitted_by:
        try:
            profile = report.submitted_by.intel_profile
        except UserProfile.DoesNotExist:
            # Auto-create profile if it somehow doesn't exist
            profile = UserProfile.objects.create(user=report.submitted_by)
        
        # Update points
        profile.total_points += points_awarded
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
        
        print(f"✅ Reward processed: {profile.user.username} earned {points_awarded} pts (Score: {score})")

    return score, points_awarded