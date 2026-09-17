import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

class CommandCenterScreen extends StatefulWidget {
  const CommandCenterScreen({Key? key}) : super(key: key);

  @override
  _CommandCenterScreenState createState() => _CommandCenterScreenState();
}

class _CommandCenterScreenState extends State<CommandCenterScreen> {
  late WebSocketChannel channel;
  final List<Map<String, dynamic>> _threats = [];
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    _connectWebSocket();
  }

  void _connectWebSocket() {
    print("🔌 Attempting to connect to WebSocket...");
    
    channel = WebSocketChannel.connect(
      Uri.parse('wss://tarabaintel-ai.onrender.com/ws/intelligence/'),
    );

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
                content: Text("🚨 NEW THREAT: ${data['report']['category']}"),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 3),
              ),
            );
          }
        } catch (e) {
          print("❌ Error parsing WebSocket message: $e");
          print("Raw message received: $message");
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
          Padding(
            padding: const EdgeInsets.all(16.0),
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
          // 1. The Map
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: LatLng(8.8833, 11.3667), // Center on Jalingo
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
            ],
          ),
          
          // 2. The Threat Feed Overlay
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