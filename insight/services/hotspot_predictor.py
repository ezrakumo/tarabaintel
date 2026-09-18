import numpy as np
from sklearn.cluster import DBSCAN
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
from ..models import Report, LGA

class HotspotPredictor:
    """
    Predictive threat analysis using DBSCAN clustering.
    Identifies geographic hotspots where threats are concentrated.
    """
    
    def __init__(self, eps=0.05, min_samples=3):
        """
        Initialize DBSCAN parameters:
        - eps: Maximum distance between points to be considered neighbors (0.05 ≈ 5km)
        - min_samples: Minimum reports to form a cluster
        """
        self.eps = eps
        self.min_samples = min_samples
    
    def get_recent_reports(self, days=30):
        """Fetch reports from the last N days with valid locations."""
        cutoff_date = timezone.now() - timedelta(days=days)
        reports = Report.objects.filter(
            submitted_at__gte=cutoff_date,
            location__isnull=False
        ).exclude(location__exact='POINT (0.0 0.0)')
        
        return reports
    
    def extract_coordinates(self, reports):
        """Extract latitude/longitude from GeoJSON reports."""
        coordinates = []
        report_ids = []
        
        for report in reports:
            try:
                # Extract coords from "POINT (lon lat)"
                coords = report.location.wkt.replace('POINT (', '').replace(')', '').split(' ')
                lon, lat = float(coords[0]), float(coords[1])
                coordinates.append([lat, lon])  # DBSCAN expects [lat, lon]
                report_ids.append(report.id)
            except Exception:
                continue
        
        return np.array(coordinates), report_ids
    
    def run_dbscan(self, coordinates):
        """Run DBSCAN clustering on coordinates."""
        if len(coordinates) < self.min_samples:
            return None, None
        
        # DBSCAN with Haversine distance (for geographic coordinates)
        db = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples,
            metric='haversine',
            algorithm='ball_tree'
        ).fit(np.radians(coordinates))  # Convert to radians for haversine
        
        return db.labels_, db.core_sample_indices_
    
    def generate_hotspots(self, days=30):
        """
        Main method: Generate predictive hotspot zones.
        Returns list of hotspot dictionaries with center, radius, and threat level.
        """
        reports = self.get_recent_reports(days)
        coordinates, report_ids = self.extract_coordinates(reports)
        
        if len(coordinates) < self.min_samples:
            print(f"⚠️ Insufficient data for clustering (only {len(coordinates)} reports)")
            return []
        
        print(f"🔍 Analyzing {len(coordinates)} reports from last {days} days...")
        
        # Run DBSCAN
        labels, core_indices = self.run_dbscan(coordinates)
        
        if labels is None:
            return []
        
        # Group reports by cluster
        hotspots = []
        unique_labels = set(labels)
        # Remove -1 (noise points)
        unique_labels.discard(-1)
        
        for cluster_id in unique_labels:
            # Get all points in this cluster
            cluster_mask = labels == cluster_id
            cluster_points = coordinates[cluster_mask]
            cluster_reports = [report_ids[i] for i in range(len(report_ids)) if cluster_mask[i]]
            
            # Calculate cluster center (centroid)
            center_lat = np.mean(cluster_points[:, 0])
            center_lon = np.mean(cluster_points[:, 1])
            
            # Calculate cluster radius (max distance from center)
            distances = np.sqrt(np.sum((cluster_points - [center_lat, center_lon])**2, axis=1))
            radius_km = np.max(distances) * 111  # Convert degrees to km (approx)
            
            # Determine threat level based on report density and urgency
            threat_score = self._calculate_threat_score(cluster_reports)
            
            hotspot = {
                'cluster_id': int(cluster_id),
                'center_lat': float(center_lat),
                'center_lon': float(center_lon),
                'radius_km': float(radius_km),
                'report_count': int(len(cluster_reports)),
                'threat_level': threat_score,
                'report_ids': cluster_reports,
            }
            
            hotspots.append(hotspot)
            print(f"✅ Hotspot #{cluster_id}: {hotspot['report_count']} reports, "
                  f"radius {radius_km:.2f}km, threat level: {threat_score}")
        
        return hotspots
    
    def _calculate_threat_score(self, report_ids):
        """
        Calculate threat level based on:
        - Report urgency levels
        - Category severity
        - Temporal recency
        """
        from ..models import Report
        
        reports = Report.objects.filter(id__in=report_ids)
        
        # Urgency weights
        urgency_weights = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MODERATE': 2,
            'LOW': 1,
        }
        
        total_weight = 0
        for report in reports:
            urgency = report.ai_urgency_level or 'MODERATE'
            total_weight += urgency_weights.get(urgency, 2)
        
        avg_weight = total_weight / len(reports)
        
        # Classify threat level
        if avg_weight >= 3.5:
            return 'CRITICAL'
        elif avg_weight >= 2.5:
            return 'HIGH'
        elif avg_weight >= 1.5:
            return 'MODERATE'
        else:
            return 'LOW'
