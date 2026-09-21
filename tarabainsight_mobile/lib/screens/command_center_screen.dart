import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'pending_verifications_screen.dart';
import 'analytics_screen.dart';

class CommandCenterScreen extends StatefulWidget {
  const CommandCenterScreen({Key? key}) : super(key: key);

  @override
  _CommandCenterScreenState createState() => _CommandCenterScreenState();
}

class _CommandCenterScreenState extends State<CommandCenterScreen> {
  late WebSocketChannel channel;
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
      print(" SECURITY BLOCK: No JWT token found. User must log in.");
      return;
    }

    String wsUrl = 'wss://tarabaintel-ai.onrender.com/ws/intelligence/?token=$token';
    print("🔑 Token attached. Connecting to: $wsUrl");

    channel = WebSocketChannel.connect(Uri.parse(wsUrl));

    channel.stream.listen(
      (message) {
        try {
          final data = jsonDecode(message);
          if (data['type'] == 'NEW_THREAT') {
            setState(() {
              _threats.add(data['report']);
            });
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(" NEW THREAT: ${data['report']['category']}"),
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
        print(" Predictive AI found ${data['hotspot_count']} hotspots");
        
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
      
      // ✅ DYNAMIC RADIUS SCALING
      // Convert km to pixels: Base scale of 100 pixels per km
      // Minimum 50px, Maximum 300px for visibility
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
    channel.sink.close();
    super.dispose();
  }

  Color _getUrgencyColor(String urgency) {
    if (urgency == 'CRITICAL') return Colors.red;
    if (urgency == 'MODERATE') return Colors.orange;
    return Colors.blue;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Taraba Command Center'),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
        actions: [
          // ✅ NEW: Pending Verifications Button
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
                MaterialPageRoute(builder: (context) => AnalyticsScreen()),
              );
            },
        ),
          // Existing LIVE Indicator
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Row(
              children: [
                Container(width: 10, height: 10, decoration: const BoxDecoration(color: Colors.green, shape: BoxShape.circle)),
                const SizedBox(width: 8),
                const Text('LIVE', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
              ],
            ),
          )
        ],
      ),
      body: Stack(
        children: [
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: LatLng(8.8833, 11.3667),
              initialZoom: 8,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                subdomains: ['a', 'b', 'c'],
              ),
              MarkerLayer(
                markers: _threats.map((threat) {
                  return Marker(
                    point: LatLng(threat['lat'], threat['lon']),
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
          
           Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            height: 200,
            child: Container(
              decoration: const BoxDecoration(
                color: Color(0xFF1F2937),
                borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
              ),
              child: Column(
                children: [
                  const Padding(
                    padding: EdgeInsets.all(12.0),
                    child: Text('LIVE INTELLIGENCE FEED', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                  Expanded(
                    child: _threats.isEmpty
                        ? const Center(child: Text('Monitoring...', style: TextStyle(color: Colors.grey)))
                        : ListView.builder(
                            itemCount: _threats.length,
                            itemBuilder: (context, index) {
                              final threat = _threats[index];
                              return ListTile(
                                leading: Icon(Icons.warning, color: _getUrgencyColor(threat['urgency'])),
                                title: Text(threat['category'], style: const TextStyle(color: Colors.white)),
                                subtitle: Text(threat['description'], maxLines: 1, style: const TextStyle(color: Colors.grey)),
                                trailing: Text(threat['urgency'], style: TextStyle(color: _getUrgencyColor(threat['urgency']), fontWeight: FontWeight.bold)),
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
        title: Text(threat['category'], style: const TextStyle(color: Colors.white)),
        content: Text(threat['description'], style: const TextStyle(color: Colors.grey)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close', style: TextStyle(color: Colors.white))),
        ],
      ),
    );
  }
}

// ✅ HOTSPOT MODEL CLASS (FIXED FOR UUID STRINGS)
class Hotspot {
  final int clusterId;
  final double centerLat;
  final double centerLon;
  final double radiusKm;
  final int reportCount;
  final String threatLevel;
  final List<String> reportIds; // ✅ CHANGED FROM List<int> TO List<String>
  
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
      // ✅ SAFELY CONVERT TO LIST OF STRINGS (UUIDs)
      reportIds: (json['report_ids'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList() ?? [],
    );
  }
}