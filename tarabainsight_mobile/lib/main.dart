import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/login_screen.dart';
import 'screens/rewards_dashboard_screen.dart';

void main() {
  runApp(const TarabaInsightApp());
}

class TarabaInsightApp extends StatelessWidget {
  const TarabaInsightApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TarabaInsight',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
      ),
      // ✅ THIS IS THE MAGIC LINE: It checks for a token first!
      home: const AuthWrapper(), 
    );
  }
}

// ✅ AUTH WRAPPER: The bouncer that decides which screen to show
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({Key? key}) : super(key: key);

  @override
  _AuthWrapperState createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoading = true;
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');
    
    print("🔍 AuthWrapper checking for token... Found: ${token != null}");

    setState(() {
      _isLoggedIn = token != null;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFF0A0E17),
        body: Center(child: CircularProgressIndicator(color: Color(0xFFEAB308))),
      );
    }

    if (_isLoggedIn) {
      print("✅ Token found! Routing to Dashboard.");
      return const RewardsDashboardScreen();
    } else {
      print("⚠️ No token found. Routing to Login Screen.");
      return LoginScreen(); // Note: NO 'const' here
    }
  }
}