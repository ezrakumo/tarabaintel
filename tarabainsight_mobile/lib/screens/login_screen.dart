import 'package:flutter/material.dart';
import '../services/reward_service.dart';
import 'rewards_dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController(text: 'ezrakumo1');
  final _passwordController = TextEditingController(text: 'SUPAUSER1@.kure2');
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _handleLogin() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    final success = await RewardService.login(
      _usernameController.text,
      _passwordController.text,
    );

    setState(() => _isLoading = false);

    if (success) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => RewardsDashboardScreen()),
      );
    } else {
      setState(() => _errorMessage = 'Invalid credentials or network error.');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Card(
            elevation: 8,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.shield, size: 64, color: Colors.blue[900]),
                  SizedBox(height: 16),
                  Text('TarabaInsight', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.blue[900])),
                  Text('Agent Portal', style: TextStyle(color: Colors.grey[600])),
                  SizedBox(height: 32),
                  TextField(
                    controller: _usernameController,
                    decoration: InputDecoration(labelText: 'Codename / Username', border: OutlineInputBorder()),
                  ),
                  SizedBox(height: 16),
                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
                  ),
                  if (_errorMessage.isNotEmpty) ...[
                    SizedBox(height: 16),
                    Text(_errorMessage, style: TextStyle(color: Colors.red)),
                  ],
                  SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _handleLogin,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue[900],
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      child: _isLoading 
                        ? CircularProgressIndicator(color: Colors.white) 
                        : Text('AUTHENTICATE', style: TextStyle(fontSize: 16, letterSpacing: 1.2)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}