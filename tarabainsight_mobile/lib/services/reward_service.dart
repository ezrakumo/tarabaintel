import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/reward_models.dart';

class RewardService {
  // YOUR LIVE RENDER URL
  static const String baseUrl = 'https://tarabaintel-ai.onrender.com/api';

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('jwt_token');
  }

  static Future<bool> login(String username, String password) async {
  // Try up to 3 times (for Render spin-up delays)
  for (int attempt = 0; attempt < 3; attempt++) {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/token/"),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      ).timeout(const Duration(seconds: 20)); // 20 second timeout

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await saveToken(data['access']);
        return true;
      }
      return false;
    } catch (e) {
      print("Login attempt ${attempt + 1} failed: $e");
      if (attempt < 2) {
        await Future.delayed(const Duration(seconds: 3)); // Wait before retry
      }
    }
  }
  return false;
}

  static Future<DashboardResponse?> getDashboard() async {
    final token = await getToken();
    if (token == null) return null;

    try {
      final response = await http.get(
        Uri.parse("$baseUrl/rewards/dashboard/"),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return DashboardResponse.fromJson(data);
      } else {
        print("Failed to load dashboard: ${response.statusCode}");
        return null;
      }
    } catch (e) {
      print("Dashboard Error: $e");
      return null;
    }
  }
}
