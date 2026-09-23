import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'rewards_dashboard_screen.dart';
import 'agent_registration_screen.dart'; // ✅ NEW IMPORT

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;

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
            SnackBar(content: Text('Login failed: ${response.body}'), backgroundColor: Colors.red),
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
        child: SingleChildScrollView( // ✅ PERFECTLY FORMATTED
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.shield, size: 80, color: Color(0xFFEAB308)),
              const SizedBox(height: 20),
              const Text('TarabaInsight', style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
              const Text('Secure Intelligence Platform', style: TextStyle(color: Colors.grey, fontSize: 16)),
              const SizedBox(height: 40),
              TextField(
                controller: _usernameController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Username',
                  labelStyle: const TextStyle(color: Colors.grey),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.grey.shade700)),
                  focusedBorder: const OutlineInputBorder(borderSide: BorderSide(color: Color(0xFFEAB308))),
                  filled: true,
                  fillColor: const Color(0xFF1F2937),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Password',
                  labelStyle: const TextStyle(color: Colors.grey),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.grey.shade700)),
                  focusedBorder: const OutlineInputBorder(borderSide: BorderSide(color: Color(0xFFEAB308))),
                  filled: true,
                  fillColor: const Color(0xFF1F2937),
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEAB308),
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.black)
                      : const Text('LOGIN', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              ),
              const SizedBox(height: 16),
              
              // ✅ NEW: BUTTON TO ACCESS AGENT REGISTRATION
              TextButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AgentRegistrationScreen()),
                  );
                },
                child: const Text(
                  'Apply to Join as Field Agent',
                  style: TextStyle(color: Color(0xFFEAB308), fontSize: 14, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}S