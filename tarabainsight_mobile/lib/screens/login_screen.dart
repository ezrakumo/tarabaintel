import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'rewards_dashboard_screen.dart';
import 'agent_registration_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true; // ✅ NEW: State variable for password visibility

  Future<void> _handleLogin() async {
    setState(() => _isLoading = true);
    final username = _usernameController.text.trim();
    final password = _passwordController.text.trim();

    print("🔥 LOGIN BUTTON PRESSED!");
    print("📦 Sending login request for: $username");

    try {
      final response = await http.post(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/token/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );

      print("📡 Login API Status: ${response.statusCode}");

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access'] ?? data['token'];
        
        print("💾 Saving token via SharedPreferences...");
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('jwt_token', token);
        print("✅ Token saved successfully!");

        print("🗺️ Fetching user profile for state mapping...");
        final profileResponse = await http.get(
          Uri.parse('https://tarabaintel-ai.onrender.com/api/auth/profile/'),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
        );

        String userState = 'TARABA'; 
        if (profileResponse.statusCode == 200) {
          final profileData = jsonDecode(profileResponse.body);
          userState = profileData['state'] ?? 'TARABA';
          print("✅ User state identified as: $userState");
        } else {
          print("⚠️ Could not fetch profile, defaulting to TARABA");
        }
        
        await prefs.setString('user_state', userState);

        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const RewardsDashboardScreen()),
          );
        }
      } else {
        print("❌ Login failed: ${response.body}");
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Login failed: Invalid credentials'), backgroundColor: Colors.red),
          );
        }
      }
    } catch (e) {
      print("💥 Login function crashed: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Network error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: const BoxDecoration(
                  color: Color(0xFFEAB308),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black38,
                      blurRadius: 15,
                      offset: Offset(0, 5),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.shield_outlined,
                  size: 80,
                  color: Color(0xFF0A0E17),
                ),
              ),
              const SizedBox(height: 30),
              const Text(
                'NigeriaInsight',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'National Intelligence Platform',
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 16,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(height: 50),
              
              TextField(
                controller: _usernameController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Username',
                  labelStyle: const TextStyle(color: Colors.grey),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade700),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: const OutlineInputBorder(
                    borderSide: BorderSide(color: Color(0xFFEAB308), width: 2),
                  ),
                  filled: true,
                  fillColor: const Color(0xFF1F2937),
                  prefixIcon: const Icon(Icons.person_outline, color: Colors.grey),
                ),
              ),
              const SizedBox(height: 20),
              
              // ✅ UPDATED PASSWORD FIELD WITH EYE ICON
              TextField(
                controller: _passwordController,
                obscureText: _obscurePassword, // ✅ DYNAMIC OBSCURING
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Password',
                  labelStyle: const TextStyle(color: Colors.grey),
                  enabledBorder: OutlineInputBorder(
                    borderSide: BorderSide(color: Colors.grey.shade700),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: const OutlineInputBorder(
                    borderSide: BorderSide(color: Color(0xFFEAB308), width: 2),
                  ),
                  filled: true,
                  fillColor: const Color(0xFF1F2937),
                  prefixIcon: const Icon(Icons.lock_outline, color: Colors.grey),
                  // ✅ EYE ICON TOGGLE
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_off : Icons.visibility,
                      color: Colors.grey,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                ),
              ),
              
              const SizedBox(height: 30),
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEAB308),
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 5,
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.black)
                      : const Text(
                          'LOGIN',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.5,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 20),
              
              TextButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AgentRegistrationScreen()),
                  );
                },
                child: const Text(
                  'Apply to Join as Field Agent',
                  style: TextStyle(
                    color: Color(0xFFEAB308),
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              
              const SizedBox(height: 30),
              const Text(
                '© 2026 NigeriaInsight. All rights reserved.',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}