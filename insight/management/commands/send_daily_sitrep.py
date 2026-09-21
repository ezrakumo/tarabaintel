from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from insight.services.intelligence_cycle import IntelligenceCycleEngine
import json

class Command(BaseCommand):
    help = 'Automated Daily SITREP dissemination to stakeholders'

    def handle(self, *args, **options):
        engine = IntelligenceCycleEngine()
        sitrep = engine.generate_daily_sitrep()
        
        # Format email content
        subject = f"🚨 TarabaInsight Daily SITREP - {sitrep['date']}"
        
        message = f"""
        TARABA STATE INTELLIGENCE SITUATION REPORT
        Date: {sitrep['date']}
        Generated: {sitrep['generated_at']}
        
        EXECUTIVE SUMMARY:
        {sitrep['executive_summary']}
        
        KEY STATISTICS:
        - Total Reports: {sitrep['statistics']['total_reports']}
        - Critical Incidents: {sitrep['statistics']['critical_incidents']}
        - Verification Rate: {sitrep['statistics']['verification_rate']}%
        - Trend: {sitrep['statistics']['trend']}
        
        HOTSPOTS:
        {chr(10).join([f"• {h['lga']}: {h['incidents']} incidents" for h in sitrep['hotspots']])}
        
        RECOMMENDATIONS:
        {chr(10).join([f"• [{r['priority']}] {r['action']}" for r in sitrep['recommendations']])}
        
        Confidence Level: {sitrep['confidence_level']}
        
        ---
        TarabaInsight Intelligence Platform
        """
        
        # Send to stakeholders
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            settings.WEEKLY_FORECAST_RECIPIENTS,
            fail_silently=False,
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Daily SITREP sent to stakeholders'))
