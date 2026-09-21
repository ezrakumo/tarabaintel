import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart'; // ✅ UNIFIED STORAGE
import '../models/reward_models.dart';

class RewardService {
  static const String baseUrl = 'https://tarabaintel-ai.onrender.com/api';

  // ✅ GET TOKEN (Matches main.dart and login_screen.dart)
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');
    
    if (token == null) {
      print("⚠️ No token found, cannot fetch dashboard");
    } else {
      print("✅ Token retrieved successfully from SharedPreferences!");
    }
    return token;
  }

  // ✅ SAVE TOKEN
  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
    print("✅ Token saved successfully!");
  }

  // ✅ LOGOUT
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    print("🚪 Token deleted (logged out)");
  }

  // ✅ FETCH DASHBOARD
  static Future<DashboardResponse?> getDashboard() async {
    final token = await getToken();
    if (token == null) return null;

    try {
      print("🔍 Fetching dashboard from: $baseUrl/rewards/dashboard/");
      
      final response = await http.get(
        Uri.parse('$baseUrl/rewards/dashboard/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      ).timeout(const Duration(seconds: 45));

      print("📡 Dashboard API Status: ${response.statusCode}");

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final dashboard = DashboardResponse.fromJson(data);
        print("✅ Dashboard parsed: ${dashboard.totalPoints} points, ${dashboard.userTier} tier");
        return dashboard;
      } else {
        print("❌ Failed to load dashboard: ${response.statusCode}");
        return null;
      }
    } catch (e) {
      print("❌ Dashboard Error: $e");
      return null;
    }
  }

  // ✅ REDEEM REWARD
  static Future<Map<String, dynamic>?> redeemReward(int rewardId) async {
    final token = await getToken();
    if (token == null) return null;

    try {
      print("🎯 Redeeming reward ID: $rewardId");
      
      final response = await http.post(
        Uri.parse('$baseUrl/rewards/redeem/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'reward_id': rewardId}),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to redeem reward: ${response.body}');
      }
    } catch (e) {
      print("❌ Redeem Error: $e");
      rethrow;
    }
  }
}