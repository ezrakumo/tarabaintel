import 'dart:convert';
import 'package:http/http.dart' as http;
import 'reward_service.dart';
import 'secure_storage_service.dart'; // ✅ Added missing import

class VerificationService {
  static const String baseUrl = 'https://tarabaintel-ai.onrender.com/api/field-verifications';

  static Future<dynamic> getPendingVerifications() async {
    final token = await RewardService.getToken();
    final url = '$baseUrl/?status=PENDING';
    print("🔍 GET Request to: $url");
    
    final response = await http.get(
      Uri.parse(url),
      headers: {'Authorization': 'Bearer $token'},
    );

    print("🔍 API Response Status: ${response.statusCode}");
    print("🔍 API Response Body: ${response.body}");

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load verifications: ${response.statusCode} - ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> claimVerification(String verificationId) async {
    if (verificationId.isEmpty) {
      throw Exception('Verification ID is missing or empty!');
    }

    final token = await RewardService.getToken();
    final agentId = await SecureStorageService().getAgentId() ?? 'AGENT_001'; // ✅ Clean, single declaration

    final url = '$baseUrl/$verificationId/claim/';
    print("🎯 POST Request to: $url");
    print("📦 Payload: ${jsonEncode({'agent_id': agentId})}");

    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'agent_id': agentId}),
    );

    print("📡 Claim Response Status: ${response.statusCode}");
    print("📡 Claim Response Body: ${response.body}");

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to claim task: ${response.statusCode} - ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> completeVerification(
    String verificationId, 
    bool isValid, 
    String notes, 
    String? imageBase64,
  ) async {
    if (verificationId.isEmpty) {
      throw Exception('Verification ID is missing or empty!');
    }

    final token = await RewardService.getToken();
    final agentId = await SecureStorageService().getAgentId() ?? 'AGENT_001'; // ✅ Clean, single declaration

    final url = '$baseUrl/$verificationId/complete/';
    print("🎯 POST Request to: $url");
    
    final payload = {
      'agent_id': agentId,
      'is_valid': isValid,
      'notes': notes,
      if (imageBase64 != null) 'image_base64': imageBase64,
    };
    print("📦 Payload: ${jsonEncode(payload)}");

    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(payload),
    );

    print("📡 Complete Response Status: ${response.statusCode}");
    print("📡 Complete Response Body: ${response.body}");

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to complete task: ${response.statusCode} - ${response.body}');
    }
  }
}