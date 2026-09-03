import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta

class IntelligenceAnalyzer:
    """Core AI Engine for TarabaInsight Intelligence Analysis"""
    
    def analyze_temporal_patterns(self, reports, days=7):
        """Detect trends over time (e.g., comparing this week to last week)"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in reports if r.submitted_at and r.submitted_at >= cutoff]
        previous = [r for r in reports if r.submitted_at and r.submitted_at < cutoff]
        
        recent_count = len(recent)
        previous_count = len(previous)
        
        # Calculate percentage change safely
        if previous_count == 0:
            change_percent = 100.0 if recent_count > 0 else 0.0
        else:
            change_percent = ((recent_count - previous_count) / previous_count) * 100
            
        # Calculate Urgency Trend
        def get_urgency_score(reps):
            scores = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}
            if not reps: return 0
            return sum(scores.get(r.ai_urgency_level or 'MEDIUM', 1) for r in reps) / len(reps)
            
        recent_score = get_urgency_score(recent)
        previous_score = get_urgency_score(previous)
        
        if recent_score > previous_score * 1.2:
            urgency_trend = 'ESCALATING'
        elif recent_score < previous_score * 0.8:
            urgency_trend = 'DE-ESCALATING'
        else:
            urgency_trend = 'STABLE'
            
        return {
            'total_recent': recent_count,
            'total_previous': previous_count,
            'change_percent': round(change_percent, 1),
            'urgency_trend': urgency_trend,
            'trend_direction': 'INCREASING' if change_percent > 10 else 'DECREASING' if change_percent < -10 else 'STABLE'
        }

    def detect_geospatial_clusters(self, reports, radius_km=5):
        """Find geographic hotspots using DBSCAN clustering"""
        # Filter reports that actually have coordinates
        valid_reports = [r for r in reports if r.location]
        if len(valid_reports) < 3:
            return [] # Need at least 3 points to form a cluster
            
        # Extract coordinates [lat, lng]
        coords = np.array([[r.location.y, r.location.x] for r in valid_reports])
        
        # DBSCAN: eps is roughly 0.045 degrees (~5km at the equator)
        clustering = DBSCAN(eps=0.045, min_samples=3).fit(coords)
        
        clusters = {}
        for i, label in enumerate(clustering.labels_):
            if label != -1: # -1 means noise/outlier
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(valid_reports[i])
        
        hotspot_analysis = []
        for cluster_id, cluster_reports in clusters.items():
            hotspot_analysis.append({
                'cluster_id': int(cluster_id),
                'report_count': len(cluster_reports),
                'center_lat': round(float(np.mean([r.location.y for r in cluster_reports])), 4),
                'center_lng': round(float(np.mean([r.location.x for r in cluster_reports])), 4),
                'categories': list(set(r.issue_category for r in cluster_reports if r.issue_category)),
                'urgency_levels': list(set(r.ai_urgency_level for r in cluster_reports if r.ai_urgency_level)),
            })
            
        # Sort by highest report count
        return sorted(hotspot_analysis, key=lambda x: x['report_count'], reverse=True)

    def generate_intelligence_summary(self, reports, period='daily'):
        """Generate the final executive intelligence package"""
        days = 1 if period == 'daily' else 7
        temporal = self.analyze_temporal_patterns(reports, days=days)
        hotspots = self.detect_geospatial_clusters(reports)
        
        # Generate Executive Briefing Text
        trend_word = "increased" if temporal['change_percent'] > 0 else "decreased"
        briefing = f"Over the past {days} day(s), intelligence collection {trend_word} by {abs(temporal['change_percent'])}%. "
        
        if hotspots:
            briefing += f"AI geospatial analysis identified {len(hotspots)} distinct threat hotspots. "
        else:
            briefing += "No significant geographic clustering detected. "
            
        if temporal['urgency_trend'] == 'ESCALATING':
            briefing += "Urgency levels are escalating, requiring immediate strategic attention."
        else:
            briefing += "Overall threat urgency remains stable."
            
        # Generate Key Findings
        key_findings = []
        if temporal['change_percent'] > 20:
            key_findings.append(f"Significant surge in reporting activity ({temporal['change_percent']}%) detected.")
        if hotspots:
            top_hotspot = hotspots[0]
            key_findings.append(f"Primary hotspot identified with {top_hotspot['report_count']} clustered incidents.")
            
        # Generate Recommendations
        recommendations = []
        if hotspots:
            recommendations.append("Deploy field verification assets to primary geographic hotspots.")
        if temporal['urgency_trend'] == 'ESCALATING':
            recommendations.append("Elevate monitoring posture and increase AI analysis frequency.")
            
        return {
            'executive_briefing': briefing,
            'key_findings': key_findings,
            'emerging_threats': [f"{h['report_count']} incidents clustered in LGA sector" for h in hotspots[:2]],
            'recommendations': recommendations,
            'statistics': {
                'total_reports': len(reports),
                'critical_incidents': len([r for r in reports if r.ai_urgency_level == 'CRITICAL']),
                'hotspots_identified': len(hotspots),
                'trend': temporal['trend_direction']
            }
        }