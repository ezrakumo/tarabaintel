class Hotspot {
  final int clusterId;
  final double centerLat;
  final double centerLon;
  final double radiusKm;
  final int reportCount;
  final String threatLevel;
  final List<int> reportIds;
  
  Hotspot({
    required this.clusterId,
    required this.centerLat,
    required this.centerLon,
    required this.radiusKm,
    required this.reportCount,
    required this.threatLevel,
    required this.reportIds,
  });
  
  factory Hotspot.fromJson(Map<String, dynamic> json) {
    return Hotspot(
      clusterId: json['cluster_id'],
      centerLat: json['center_lat'],
      centerLon: json['center_lon'],
      radiusKm: json['radius_km'],
      reportCount: json['report_count'],
      threatLevel: json['threat_level'],
      reportIds: List<int>.from(json['report_ids']),
    );
  }
}