from django.utils import timezone
from datetime import timedelta
from insight.models import Report, IntelligenceSummary, PatternAlert
from insight.services.intelligence_analyzer import IntelligenceAnalyzer

class IntelligenceGenerationService:
    def __init__(self):
        self.analyzer = IntelligenceAnalyzer()
    
    def generate_daily_sitrep(self):
        """Generate and save a Daily Situation Report"""
        yesterday = timezone.now() - timedelta(days=1)
        reports = Report.objects.filter(submitted_at__gte=yesterday)
        
        if reports.count() == 0:
            return None
            
        # Run AI Analysis
        summary_data = self.analyzer.generate_intelligence_summary(list(reports), period='daily')
        
        # Save to Database
        summary = IntelligenceSummary.objects.create(
            title=f"Daily SITREP - {yesterday.strftime('%Y-%m-%d')}",
            period_type='DAILY',
            period_start=yesterday,
            period_end=timezone.now(),
            executive_briefing=summary_data['executive_briefing'],
            key_findings=summary_data['key_findings'],
            emerging_threats=summary_data['emerging_threats'],
            recommendations=summary_data['recommendations'],
            statistics=summary_data['statistics'],
        )
        
        summary.source_reports.set(reports)
        return summary

    def check_for_alerts(self):
        """Scan recent reports and trigger Pattern Alerts if thresholds are met"""
        recent_24h = Report.objects.filter(submitted_at__gte=timezone.now() - timedelta(hours=24))
        
        # 1. Check for Volume Surge (Threshold: > 10 reports in 24h)
        if recent_24h.count() > 10:
            PatternAlert.objects.create(
                alert_type='SURGE',
                severity='WARNING',
                title='High Report Volume Detected',
                description=f'{recent_24h.count()} reports submitted in the last 24 hours.',
                pattern_data={'count': recent_24h.count()}
            )
            
        # 2. Check for Geographic Clusters
        hotspots = self.analyzer.detect_geospatial_clusters(list(recent_24h))
        for hotspot in hotspots:
            if hotspot['report_count'] >= 3:
                is_critical = 'CRITICAL' in hotspot.get('urgency_levels', [])
                PatternAlert.objects.create(
                    alert_type='CLUSTER',
                    severity='CRITICAL' if is_critical else 'WARNING',
                    title='Geographic Hotspot Detected',
                    description=f"{hotspot['report_count']} incidents clustered at Lat: {hotspot['center_lat']}, Lng: {hotspot['center_lng']}",
                    pattern_data=hotspot
                )