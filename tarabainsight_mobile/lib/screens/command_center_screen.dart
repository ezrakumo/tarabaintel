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

  // ✅ DYNAMIC STATE CENTERING
  String _userState = 'TARABA';
  LatLng _initialCenter = const LatLng(8.8833, 11.3667);
  double _initialZoom = 8.0;

  @override
  void initState() {
    super.initState();
    _loadUserStateAndInit();
  }

  Future<void> _loadUserStateAndInit() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    String? state = prefs.getString('user_state');

    // ✅ DYNAMICALLY SET MAP CENTER BASED ON THE ACTUAL LOGGED-IN USER'S STATE
    // If 'user_state' is missing in storage, it safely defaults to 'TARABA'
    String targetState = state ?? 'TARABA'; 
    
    if (targetState == 'DELTA') {
      _userState = 'DELTA';
      _initialCenter = const LatLng(5.8000, 6.0000); // Approximate center of Delta State
      _initialZoom = 8.5;
    } else {
      _userState = 'TARABA';
      _initialCenter = const LatLng(8.8833, 11.3667); // Approximate center of Taraba State
      _initialZoom = 8.0;
    }
    
    if (mounted) {
      setState(() {}); // Update UI variables
      
      // ✅ CRITICAL FIX: Force the map controller to physically move to the new center!
      Future.delayed(const Duration(milliseconds: 200), () {
        if (mounted) {
          _mapController.move(_initialCenter, _initialZoom);
        }
      });
    }

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
      
      switch (hotspot.severity) {
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
      
      return CircleMarker(
        point: LatLng(hotspot.lat, hotspot.lon),
        radius: 60.0, // Fixed radius for clear visibility on the map
        color: circleColor,
        borderColor: borderColor,
        borderStrokeWidth: 2,
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
        // ✅ DYNAMIC TITLE BASED ON STATE
        title: Text('$_userState Command Center', style: const TextStyle(fontWeight: FontWeight.bold)),
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
            key: ValueKey(_userState), // ✅ FORCES COMPLETE REBUILD WHEN STATE CHANGES
            mapController: _mapController,
            options: MapOptions(
              initialCenter: _initialCenter, // ✅ DYNAMIC CENTER
              initialZoom: _initialZoom,     // ✅ DYNAMIC ZOOM
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                subdomains: const ['a', 'b', 'c'],
              ),
              MarkerLayer(
                markers: _threats.map((threat) {
                  return Marker(
                    point: LatLng(threat['lat'] ?? _initialCenter.latitude, threat['lon'] ?? _initialCenter.longitude),
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

// ✅ EXTRACTED TOP CARD TO A SEPARATE WIDGET FOR CLEANER CODE
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

// ✅ UPDATED HOTSPOT MODEL TO MATCH BACKEND API RESPONSE
class Hotspot {
  final double lat;
  final double lon;
  final String category;
  final String severity;
  final String state;

  Hotspot({
    required this.lat,
    required this.lon,
    required this.category,
    required this.severity,
    required this.state,
  });

  factory Hotspot.fromJson(Map<String, dynamic> json) {
    return Hotspot(
      lat: (json['lat'] ?? 0.0).toDouble(),
      lon: (json['lon'] ?? 0.0).toDouble(),
      category: json['category'] ?? 'Unknown',
      severity: json['severity'] ?? 'MODERATE',
      state: json['state'] ?? 'TARABA',
    );
  }
}