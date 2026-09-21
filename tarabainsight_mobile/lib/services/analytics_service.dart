import 'dart:convert';
import 'package:http/http.dart' as http;
import 'reward_service.dart';

class AnalyticsService {
  static const String baseUrl = 'https://tarabaintel-ai.onrender.com/api';

  static Future<Map<String, dynamic>?> getPerformance() async {
    final token = await RewardService.getToken();
    if (token == null) return null;

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/analytics/agent-performance/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        print("❌ Analytics API Error: ${response.statusCode}");
        return null;
      }
    } catch (e) {
      print("❌ Analytics Fetch Error: $e");
      return null;
    }
  }
}