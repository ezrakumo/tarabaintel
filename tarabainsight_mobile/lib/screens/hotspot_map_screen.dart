import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class HotspotMapScreen extends StatefulWidget {
  const HotspotMapScreen({Key? key}) : super(key: key);

  @override
  _HotspotMapScreenState createState() => _HotspotMapScreenState();
}

class _HotspotMapScreenState extends State<HotspotMapScreen> {
  List<Map<String, dynamic>> _hotspots = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchHotspots();
  }

  Future<void> _fetchHotspots() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');
      
      final response = await http.get(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/predictive-hotspots/'),
        headers: {'Authorization': 'Bearer $token'},
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _hotspots = List<Map<String, dynamic>>.from(data['hotspots'] ?? []);
          _isLoading = false;
        });
      } else {
        setState(() { _error = 'Failed to load map data'; _isLoading = false; });
      }
    } catch (e) {
      setState(() { _error = 'Network error'; _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Threat Hotspot Map', style: TextStyle(color: Colors.white)),
        backgroundColor: const Color(0xFF1F2937),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _fetchHotspots)],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.amber))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
              : _hotspots.isEmpty
                  ? const Center(child: Text('No active threats detected.', style: TextStyle(color: Colors.white)))
                  : FlutterMap(
                      options: MapOptions(
                        initialCenter: LatLng(8.8833, 11.3667), // ✅ CENTERED ON JALINGO
                        initialZoom: 9.0, // ✅ ZOOMED IN CLOSER
                      ),
                      children: [
                        TileLayer(
                          urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                          subdomains: const ['a', 'b', 'c'],
                        ),
                        MarkerLayer(
                          markers: _hotspots.map((spot) {
                            final isCritical = spot['severity'] == 'CRITICAL';
                            return Marker(
                              point: LatLng(spot['lat'], spot['lon']),
                              width: 30.0, // ✅ SMALLER MARKER
                              height: 30.0,
                              child: Icon(
                                Icons.place,
                                color: isCritical ? Colors.red : Colors.orange,
                                size: 30, // ✅ SMALLER ICON
                              ),
                            );
                          }).toList(),
                        ),
                        CircleLayer(
                          circles: _hotspots.map((spot) {
                            final isCritical = spot['severity'] == 'CRITICAL';
                            return CircleMarker(
                              point: LatLng(spot['lat'], spot['lon']),
                              radius: 15.0, // ✅ SMALLER RADIUS (Was 40.0)
                              color: isCritical ? Colors.red.withOpacity(0.2) : Colors.orange.withOpacity(0.2),
                              borderStrokeWidth: 1.0,
                              borderColor: isCritical ? Colors.red : Colors.orange,
                            );
                          }).toList(),
                        ),
                      ],
                    ),
    );
  }
}