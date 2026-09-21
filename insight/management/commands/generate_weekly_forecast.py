from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from insight.services.hotspot_predictor import HotspotPredictor
from insight.models import Report

class Command(BaseCommand):
    help = 'Generate and email the Weekly Threat Forecast to command staff.'
    
    def handle(self, *args, **options):
        self.stdout.write("🧠 Initializing Weekly Threat Forecast...")
        
        # 1. Run AI Predictor for the last 7 days (using our tuned sensitivity)
        predictor = HotspotPredictor(eps=0.02, min_samples=2)
        hotspots = predictor.generate_hotspots(days=7)
        
        # 2. Gather basic stats for the executive summary
        total_reports = Report.objects.filter(
            submitted_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        critical_hotspots = [h for h in hotspots if h['threat_level'] in ['CRITICAL', 'HIGH']]
        
        # 3. Format the Email Content
        subject = f"🚨 WEEKLY INTELLIGENCE FORECAST: {len(critical_hotspots)} High-Risk Zones Identified"
        
        message = f"""TARABA STATE INTELLIGENCE COMMAND
Weekly Threat Forecast & Situational Awareness Report
Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================

📊 EXECUTIVE SUMMARY
- Total Reports Analyzed (Last 7 Days): {total_reports}
- Active Threat Hotspots Identified: {len(hotspots)}
- High/Critical Risk Zones: {len(critical_hotspots)}

🔥 PREDICTIVE HOTSPOTS REQUIRING ATTENTION
"""
        if not critical_hotspots:
            message += "- No critical or high-risk clusters detected this week. Maintain standard patrol routines.\n"
        else:
            for i, hotspot in enumerate(critical_hotspots, 1):
                message += f"""
{i}. ZONE {hotspot['cluster_id']} ({hotspot['threat_level']} RISK)
   - Location: Lat {hotspot['center_lat']:.4f}, Lon {hotspot['center_lon']:.4f}
   - Estimated Radius: {hotspot['radius_km']:.2f} km
   - Incident Density: {hotspot['report_count']} reports clustered
   - Recommended Action: Increase patrol visibility and establish temporary checkpoints in this radius.
"""

        message += """
================================================================
🛡️ STRATEGIC RECOMMENDATIONS
1. Deploy rapid response units to the High/Critical zones listed above.
2. Task field agents to verify the legitimacy of clustered reports in these LGAs.
3. Review the TarabaInsight Command Dashboard for real-time map visualization: https://tarabaintel-ai.onrender.com/command-dashboard/

This is an automated message from the TarabaInsight AI Engine.
"""
        
        # 4. Send the Email (Uses settings or falls back to default)
        recipient_list = getattr(settings, 'WEEKLY_FORECAST_RECIPIENTS', ['ops@tarabaintel.gov.ng', 'admin@tarabaintel.gov.ng'])
        
        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@tarabaintel.com'),
                recipient_list,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Weekly forecast successfully emailed to {len(recipient_list)} recipient(s).'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to send email: {e}'))
