import 'dart:convert';
import 'package:http/http.dart' as http;
import 'reward_service.dart'; // Reusing the token logic

class ReportService {
  static const String baseUrl = 'https://tarabaintel-ai.onrender.com/api';

  static Future<Map<String, dynamic>?> submitReport({
    required String description,
    required String issueCategory,
    required String lgaName,
    String? locationDetails,
  }) async {
    final token = await RewardService.getToken();
    if (token == null) return null;

    try {
      // Note: The backend expects 'lga' as an ID, but for MVP we will send the name 
      // and let the backend handle it, OR we can just send the text. 
      // To ensure it works perfectly with your current backend, we'll send the exact payload.
      final payload = {
        "description": description,
        "issue_category": issueCategory,

        // If your backend strictly requires an LGA ID, we might need to fetch LGAs first. 
        // For now, we'll omit 'lga' ID to prevent 400 errors, or you can add it if you have the ID.
      };

      final response = await http.post(
        Uri.parse("$baseUrl/reports/"),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(payload),
      ).timeout(const Duration(seconds: 30)); // AI analysis takes time!

      if (response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        print("Submission failed: ${response.body}");
        return null;
      }
    } catch (e) {
      print("Report Submission Error: $e");
      return null;
    }
  }
}