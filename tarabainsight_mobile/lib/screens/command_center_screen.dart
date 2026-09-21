import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'pending_verifications_screen.dart';
import 'analytics_screen.dart';
import 'stakeholder_dashboard_screen.dart';

class CommandCenterScreen extends StatefulWidget {
  const CommandCenterScreen({Key? key}) : super(key: key);

  @override
  _CommandCenterScreenState createState() => _CommandCenterScreenState();
}

class _CommandCenterScreenState extends State<CommandCenterScreen> {
  WebSocketChannel? channel;
  final List<Map<String, dynamic>> _threats = [];
  final MapController _mapController = MapController();
  List<Hotspot> _hotspots = [];

  @override
  void initState() {
    super.initState();
    _connectWebSocket();
    _fetchPredictiveHotspots();
  }

  Future<void> _connectWebSocket() async {
    print("🔌 Attempting to connect to secure WebSocket...");
    
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? token = prefs.getString('jwt_token'); 
    
    if (token == null || token.isEmpty) {
      print("🛡️ SECURITY BLOCK: No JWT token found. User must log in.");
      return;
    }

    String wsUrl = 'wss://tarabaintel-ai.onrender.com/ws/intelligence/?token=$token';
    print("🔑 Token attached. Connecting to: $wsUrl");

    channel = WebSocketChannel.connect(Uri.parse(wsUrl));

    channel!.stream.listen(
      (message) {
        try {
          final data = jsonDecode(message);
          if (data['type'] == 'NEW_THREAT') {
            setState(() {
              _threats.add(data['report']);
            });
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text("🚨 NEW THREAT: ${data['report']['category']}"),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 3),
              ),
            );
          }
        } catch (e) {
          print("❌ Error parsing WebSocket message: $e");
        }
      },
      onError: (error) {
        print("❌ WebSocket Connection Error: $error");
      },
      onDone: () {
        print("⚠️ WebSocket Connection Closed");
      },
    );
  }

  Future<void> _fetchPredictiveHotspots() async {
    try {
      SharedPreferences prefs = await SharedPreferences.getInstance();
      String? token = prefs.getString('jwt_token'); 
      
      if (token == null || token.isEmpty) {
        print("⚠️ No token found for hotspot API request.");
        return;
      }

      final response = await http.get(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/predictive-hotspots/?days=30'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print("🤖 Predictive AI found ${data['hotspot_count']} hotspots");
        
        setState(() {
          _hotspots = (data['hotspots'] as List).map((h) => Hotspot.fromJson(h)).toList();
        });
      } else {
        print("⚠️ Failed to fetch hotspots: ${response.statusCode}");
      }
    } catch (e) {
      print("❌ Error fetching hotspots: $e");
    }
  }

  List<CircleMarker> _buildHotspotCircles() {
    return _hotspots.map((hotspot) {
      Color circleColor;
      Color borderColor;
      
      switch (hotspot.threatLevel) {
        case 'CRITICAL':
          circleColor = Colors.red.withOpacity(0.4);
          borderColor = Colors.red;
          break;
        case 'HIGH':
          circleColor = Colors.orange.withOpacity(0.4);
          borderColor = Colors.orange;
          break;
        default:
          circleColor = Colors.yellow.withOpacity(0.4);
          borderColor = Colors.yellow;
      }
      
      double radiusInPixels = (hotspot.radiusKm * 100).clamp(50.0, 300.0);
      
      return CircleMarker(
        point: LatLng(hotspot.centerLat, hotspot.centerLon),
        radius: radiusInPixels,
        color: circleColor,
        borderColor: borderColor,
        borderStrokeWidth: 3,
      );
    }).toList();
  }
  
  @override
  void dispose() {
    channel?.sink.close();
    super.dispose();
  }

  Color _getUrgencyColor(String? urgency) {
    if (urgency == 'CRITICAL') return Colors.red;
    if (urgency == 'HIGH') return Colors.orange;
    if (urgency == 'MODERATE') return Colors.orange;
    return Colors.blue;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Taraba Command Center', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.task_alt, color: Colors.amber),
            tooltip: 'Pending Verifications',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const PendingVerificationsScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.analytics, color: Colors.greenAccent),
            tooltip: 'Performance Analytics',
            onPressed: () {
              Navigator.push(
                context, 
                MaterialPageRoute(builder: (context) => const AnalyticsScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.assessment, color: Colors.purpleAccent),
            tooltip: 'Intelligence Dashboard',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const StakeholderDashboardScreen()),
              );
            },
          ),
          const Padding(
            padding: EdgeInsets.only(right: 16.0),
            child: Row(
              children: [
                SizedBox(width: 8, height: 8, child: DecoratedBox(decoration: BoxDecoration(color: Colors.green, shape: BoxShape.circle))),
                SizedBox(width: 8),
                Text('LIVE', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 12)),
              ],
            ),
          )
        ],
      ),
      body: Stack(
        children: [
          // 1. BASE LAYER: THE MAP
          FlutterMap(
            mapController: _mapController,
            options: const MapOptions(
              initialCenter: LatLng(8.8833, 11.3667),
              initialZoom: 8,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                subdomains: const ['a', 'b', 'c'],
              ),
              MarkerLayer(
                markers: _threats.map((threat) {
                  return Marker(
                    point: LatLng(threat['lat'] ?? 8.8833, threat['lon'] ?? 11.3667),
                    width: 40,
                    height: 40,
                    child: GestureDetector(
                      onTap: () => _showThreatDetails(threat),
                      child: Icon(
                        Icons.place,
                        color: _getUrgencyColor(threat['urgency']),
                        size: 40,
                      ),
                    ),
                  );
                }).toList(),
              ),
              CircleLayer(circles: _buildHotspotCircles()),
            ],
          ),
          
          // 2. TOP FLOATING CARD: INTELLIGENCE DASHBOARD QUICK LINK
          const Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: _DashboardQuickLinkCard(),
          ),

          // 3. BOTTOM FLOATING CARD: LIVE INTELLIGENCE FEED
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            height: 200,
            child: Container(
              // ✅ NO 'const' HERE, ALLOWING DYNAMIC OPACITY CALCULATION
              decoration: BoxDecoration(
                color: const Color(0xFF1F2937),
                borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.5),
                    blurRadius: 10,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  const Padding(
                    padding: EdgeInsets.all(12.0),
                    child: Text('LIVE INTELLIGENCE FEED', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                  Expanded(
                    child: _threats.isEmpty
                        ? const Center(child: Text('Monitoring airspace...', style: TextStyle(color: Colors.grey)))
                        : ListView.builder(
                            itemCount: _threats.length,
                            itemBuilder: (context, index) {
                              final threat = _threats[index];
                              return ListTile(
                                leading: Icon(Icons.warning, color: _getUrgencyColor(threat['urgency'])),
                                title: Text(threat['category'] ?? 'Unknown', style: const TextStyle(color: Colors.white)),
                                subtitle: Text(threat['description'] ?? 'No description', maxLines: 1, style: const TextStyle(color: Colors.grey)),
                                trailing: Text(threat['urgency'] ?? 'MODERATE', style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showThreatDetails(Map<String, dynamic> threat) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1F2937),
        title: Text(threat['category'] ?? 'Unknown Threat', style: const TextStyle(color: Colors.white)),
        content: Text(threat['description'] ?? 'No details available.', style: const TextStyle(color: Colors.grey)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context), 
            child: const Text('Close', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}

// ✅ EXTRACTED TOP CARD TO A SEPARATE WIDGET FOR CLEANER CODE & NO CONST ERRORS
class _DashboardQuickLinkCard extends StatelessWidget {
  const _DashboardQuickLinkCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF7C3AED), Color(0xFF6D28D9)]),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(Icons.analytics, color: Colors.white, size: 32),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Intelligence Dashboard', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                Text('Real-time KPIs & Active Threats', style: TextStyle(color: Colors.white70, fontSize: 12)),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.arrow_forward, color: Colors.white),
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (context) => const StakeholderDashboardScreen()));
            },
          ),
        ],
      ),
    );
  }
}

// ✅ HOTSPOT MODEL CLASS
class Hotspot {
  final int clusterId;
  final double centerLat;
  final double centerLon;
  final double radiusKm;
  final int reportCount;
  final String threatLevel;
  final List<String> reportIds;
  
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
      clusterId: json['cluster_id'] ?? 0,
      centerLat: (json['center_lat'] ?? 0.0).toDouble(),
      centerLon: (json['center_lon'] ?? 0.0).toDouble(),
      radiusKm: (json['radius_km'] ?? 0.0).toDouble(),
      reportCount: json['report_count'] ?? 0,
      threatLevel: json['threat_level'] ?? 'MODERATE',
      reportIds: (json['report_ids'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
    );
  }
}