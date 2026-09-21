import 'dart:convert';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'offline_db.dart';

class SyncService {
  static final SyncService instance = SyncService._init();
  
  SyncService._init() {
    _listenToConnectivity();
  }

  void _listenToConnectivity() {
    // Listen for network changes (connectivity_plus v5+ returns a List)
    Connectivity().onConnectivityChanged.listen((List<ConnectivityResult> results) {
      final hasConnection = results.any((result) => result != ConnectivityResult.none);
      
      if (hasConnection) {
        print("🌐 Network restored! Attempting to sync offline reports...");
        syncOfflineReports();
      }
    });
  }

  Future<void> syncOfflineReports() async {
    final unsyncedReports = await OfflineDb.instance.getUnsyncedReports();
    if (unsyncedReports.isEmpty) {
      print("✅ No offline reports to sync.");
      return;
    }

    print("🔄 Found ${unsyncedReports.length} offline reports to sync.");
    
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');

    if (token == null) {
      print("⚠️ Cannot sync: User is not logged in (no JWT token).");
      return;
    }

    for (var report in unsyncedReports) {
      try {
        final response = await http.post(
          Uri.parse('https://tarabaintel-ai.onrender.com/api/reports/'),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'issue_category': report['category'],
            'description': report['description'],
            'lga_name': report['lga'], // Adjust if your backend expects 'lga'
            'lat': report['lat'],
            'lon': report['lon'],
            'image_base64': report['image_base64'], // ✅ ADDED FOR SEAMLESS SYNC
            'is_covert': false,
            // Note: If you store images offline, read the file and convert to base64 here
          }),
        );

        if (response.statusCode == 201) {
          // Successfully synced, delete from local DB
          await OfflineDb.instance.deleteReport(report['id']);
          print("✅ Synced report: ${report['id']}");
        } else {
          print("⚠️ Failed to sync report ${report['id']}: ${response.statusCode}");
        }
      } catch (e) {
        print("❌ Error syncing report ${report['id']}: $e");
      }
    }
  }
}