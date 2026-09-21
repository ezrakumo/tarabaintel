from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from ..models import Report, FieldVerification, IntelligenceSummary

class IntelligenceCycleEngine:
    """
    Implements the 5-phase Intelligence Cycle to produce actionable reports
    """
    
    def generate_daily_sitrep(self):
        """
        PHASE 3-5: Process, Analyze, and Disseminate Daily Situation Report
        """
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # PHASE 3: PROCESSING - Aggregate raw data
        reports_24h = Report.objects.filter(
            submitted_at__date=yesterday
        )
        
        # Categorize by urgency
        critical_count = reports_24h.filter(ai_urgency_level='CRITICAL').count()
        high_count = reports_24h.filter(ai_urgency_level='HIGH').count()
        moderate_count = reports_24h.filter(ai_urgency_level='MODERATE').count()
        
        # Top 3 LGAs with most activity
        top_lgas = reports_24h.values('lga__name').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        # PHASE 4: ANALYSIS - Identify patterns
        verified_reports = FieldVerification.objects.filter(
            status='COMPLETED',
            completed_at__date=yesterday
        )
        
        verification_rate = (
            verified_reports.filter(is_valid=True).count() / 
            verified_reports.count() * 100
        ) if verified_reports.exists() else 0
        
        # Trend analysis (compared to previous day)
        prev_day_count = Report.objects.filter(
            submitted_at__date=(yesterday - timedelta(days=1))
        ).count()
        
        trend = "INCREASING" if reports_24h.count() > prev_day_count else "DECREASING"
        
        # PHASE 5: DISSEMINATION - Generate structured SITREP
        sitrep = {
            'report_type': 'DAILY_SITREP',
            'date': yesterday.strftime('%Y-%m-%d'),
            'generated_at': timezone.now().isoformat(),
            'executive_summary': self._generate_executive_summary(
                reports_24h.count(), critical_count, trend
            ),
            'statistics': {
                'total_reports': reports_24h.count(),
                'critical_incidents': critical_count,
                'high_priority': high_count,
                'moderate_priority': moderate_count,
                'verification_rate': round(verification_rate, 1),
                'trend': trend,
            },
            'hotspots': [
                {'lga': item['lga__name'] or 'Unknown', 'incidents': item['count']}
                for item in top_lgas
            ],
            'recommendations': self._generate_recommendations(
                critical_count, verification_rate, trend
            ),
            'confidence_level': 'HIGH' if reports_24h.count() > 10 else 'MEDIUM'
        }
        
        # Save to database for historical tracking
        IntelligenceSummary.objects.create(
            generated_at=timezone.now(),
            summary_type='DAILY',
            title=f"Daily SITREP - {yesterday.strftime('%b %d, %Y')}",
            content=sitrep,
            statistics=sitrep['statistics']
        )
        
        return sitrep
    
    def _generate_executive_summary(self, total, critical, trend):
        """Generate human-readable executive summary"""
        if critical > 0:
            return (f"ALERT: {critical} critical incidents reported in last 24h. "
                   f"Overall trend: {trend}. Immediate attention required.")
        elif total > 20:
            return (f"High volume of intelligence received ({total} reports). "
                   f"Trend: {trend}. Enhanced monitoring recommended.")
        else:
            return f"Routine intelligence collection. {total} reports received. Trend: {trend}."
    
    def _generate_recommendations(self, critical, verification_rate, trend):
        """Generate actionable recommendations for stakeholders"""
        recommendations = []
        
        if critical > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Deploy rapid response teams to verified critical incident locations',
                'timeline': 'Immediate (0-2 hours)'
            })
        
        if verification_rate < 50:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Review field agent training - low verification rate detected',
                'timeline': 'Within 24 hours'
            })
        
        if trend == "INCREASING":
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Increase collection capacity in high-activity LGAs',
                'timeline': 'Within 48 hours'
            })
        
        return recommendations
    
    def detect_patterns(self, days=7):
        """
        PHASE 4: Advanced Pattern Detection
        Identifies emerging threats and anomalies
        """
        since = timezone.now() - timedelta(days=days)
        
        # Pattern 1: Spike Detection (sudden increase in specific category)
        category_counts = Report.objects.filter(
            submitted_at__gte=since
        ).values('issue_category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        patterns = []
        for cat in category_counts:
            if cat['count'] > 10:  # Threshold for pattern detection
                patterns.append({
                    'pattern_type': 'VOLUME_SPIKE',
                    'category': cat['issue_category'],
                    'count': cat['count'],
                    'severity': 'HIGH' if cat['count'] > 20 else 'MEDIUM',
                    'recommendation': f"Investigate surge in {cat['issue_category']} reports"
                })
        
        # Pattern 2: Geographic Clustering
        lga_clusters = Report.objects.filter(
            submitted_at__gte=since,
            location__isnull=False
        ).values('lga__name').annotate(
            count=Count('id'),
            critical_count=Count('id', filter=Q(ai_urgency_level='CRITICAL'))
        ).filter(count__gte=5)
        
        for cluster in lga_clusters:
            if cluster['critical_count'] > 0:
                patterns.append({
                    'pattern_type': 'GEOGRAPHIC_HOTSPOT',
                    'location': cluster['lga__name'],
                    'total_incidents': cluster['count'],
                    'critical_incidents': cluster['critical_count'],
                    'severity': 'CRITICAL',
                    'recommendation': f"Deploy resources to {cluster['lga__name']} - active hotspot"
                })
        
        return patterns