from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from insight.services.hotspot_predictor import HotspotPredictor

class Command(BaseCommand):
    help = 'Generate and email weekly threat forecast'
    
    def handle(self, *args, **options):
        predictor = HotspotPredictor(eps=0.05, min_samples=3)
        hotspots = predictor.generate_hotspots(days=7)
        
        critical_hotspots = [h for h in hotspots if h['threat_level'] == 'CRITICAL']
        
        subject = f"🚨 WEEKLY THREAT FORECAST: {len(critical_hotspots)} Critical Hotspots Identified"
        
        message = f"""
TARABA STATE INTELLIGENCE FORECAST
Generated: {timezone.now()}

CRITICAL HOTSPOTS REQUIRING IMMEDIATE ATTENTION:
"""
        for hotspot in critical_hotspots:
            message += f"""
- Cluster #{hotspot['cluster_id']}: {hotspot['report_count']} reports
  Location: {hotspot['center_lat']:.4f}, {hotspot['center_lon']:.4f}
  Radius: {hotspot['radius_km']:.2f}km
  Threat Level: {hotspot['threat_level']}
"""

        send_mail(
            subject,
            message,
            'noreply@tarabaintel.com',
            ['ops@tarabaintel.gov.ng'],
            fail_silently=False,
        )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Weekly forecast sent! {len(hotspots)} hotspots identified.'))
