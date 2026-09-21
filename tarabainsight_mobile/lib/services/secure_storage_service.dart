import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageService {
  final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true, // ✅ Extra encryption layer
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );

  // ✅ SAVE TOKEN SECURELY
  Future<void> saveToken(String token) async {
    await _storage.write(key: 'jwt_token', value: token);
    print("✅ Token saved securely");
  }

  // ✅ RETRIEVE TOKEN SECURELY
  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt_token');
  }

  // ✅ DELETE TOKEN (LOGOUT)
  Future<void> deleteToken() async {
    await _storage.delete(key: 'jwt_token');
    print("🚪 Token deleted (logged out)");
  }

  // ✅ SAVE AGENT ID
  Future<void> saveAgentId(String agentId) async {
    await _storage.write(key: 'agent_id', value: agentId);
  }

  // ✅ RETRIEVE AGENT ID
  Future<String?> getAgentId() async {
    return await _storage.read(key: 'agent_id');
  }
}