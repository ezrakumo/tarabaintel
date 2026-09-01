import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:typed_data';

void main() {
  runApp(const TarabaInsightApp());
}

class TarabaInsightApp extends StatelessWidget {
  const TarabaInsightApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TarabaInsight',
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
        brightness: Brightness.dark,
      ),
      home: const AuthWrapper(),
    );
  }
}

// 1. AUTH WRAPPER: Decides whether to show Login or Report screen
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});
  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoading = true;
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  Future<void> _checkLoginStatus() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');
    setState(() {
      _isLoggedIn = token != null;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return _isLoggedIn ? const CitizenReportScreen() : const LoginScreen();
  }
}

// 2. LOGIN SCREEN
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _login() async {
    setState(() { _isLoading = true; _errorMessage = ''; });

    try {
      final response = await http.post(
        Uri.parse('https://tarabaintel.onrender.com/api/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': _usernameController.text,
          'password': _passwordController.text,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('jwt_token', data['access']);
        
        setState(() { _isLoading = false; });
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const CitizenReportScreen()));
      } else {
        setState(() {
          _isLoading = false;
          _errorMessage = 'Invalid username or password';
        });
      }
    } catch (e) {
      setState(() { _isLoading = false; _errorMessage = 'Network error. Check your connection.'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('TarabaInsight Login'), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Welcome Back', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Enter your credentials to submit reports.', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 32),
            TextField(controller: _usernameController, decoration: const InputDecoration(labelText: 'Username', border: OutlineInputBorder())),
            const SizedBox(height: 16),
            TextField(controller: _passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder())),
            const SizedBox(height: 24),
            if (_errorMessage.isNotEmpty) Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _login,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
              child: _isLoading ? const CircularProgressIndicator() : const Text('LOGIN', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen()));
              },
              child: const Text('Don\'t have an account? Register here'),
            )
          ],
        ),
      ),
    );
  }
}

// 3. NEW: REGISTRATION SCREEN
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  String _selectedRole = 'CITIZEN';
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _register() async {
    if (_usernameController.text.isEmpty || _passwordController.text.length < 8) {
      setState(() { _errorMessage = 'Username required. Password must be 8+ characters.'; });
      return;
    }

    setState(() { _isLoading = true; _errorMessage = ''; });

    try {
      final response = await http.post(
        Uri.parse('https://tarabaintel.onrender.com/api/auth/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': _usernameController.text,
          'email': _emailController.text,
          'password': _passwordController.text,
          'role': _selectedRole,
        }),
      );

      if (response.statusCode == 201) {
        // Success! Navigate back to login
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Registration successful! Please log in.'), backgroundColor: Colors.green),
        );
        Navigator.pop(context); // Go back to Login screen
      } else {
        final errorData = jsonDecode(response.body);
        setState(() {
          _isLoading = false;
          // Extract the first error message from Django's response
          _errorMessage = errorData.values.first.first.toString(); 
        });
      }
    } catch (e) {
      setState(() { _isLoading = false; _errorMessage = 'Network error. Check your connection.'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account'), centerTitle: true),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Join TarabaInsight', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('Register as a Citizen or Field Agent.', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 32),
            TextField(controller: _usernameController, decoration: const InputDecoration(labelText: 'Username', border: OutlineInputBorder())),
            const SizedBox(height: 16),
            TextField(controller: _emailController, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email (Optional)', border: OutlineInputBorder())),
            const SizedBox(height: 16),
            TextField(controller: _passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Password (Min 8 chars)', border: OutlineInputBorder())),
            const SizedBox(height: 24),
            
            // Role Selection
            const Text('Select Your Role:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: RadioListTile<String>(
                    title: const Text('Citizen'),
                    value: 'CITIZEN',
                    groupValue: _selectedRole,
                    onChanged: (val) => setState(() => _selectedRole = val!),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
                Expanded(
                  child: RadioListTile<String>(
                    title: const Text('Field Agent'),
                    value: 'AGENT',
                    groupValue: _selectedRole,
                    onChanged: (val) => setState(() => _selectedRole = val!),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (_errorMessage.isNotEmpty) Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            
            ElevatedButton(
              onPressed: _isLoading ? null : _register,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
              child: _isLoading ? const CircularProgressIndicator() : const Text('REGISTER', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}

// 4. REPORT SCREEN (Unchanged, but included for completeness)
class CitizenReportScreen extends StatefulWidget {
  const CitizenReportScreen({super.key});
  @override
  State<CitizenReportScreen> createState() => _CitizenReportScreenState();
}

class _CitizenReportScreenState extends State<CitizenReportScreen> {
  final _descriptionController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  
  bool _isLoading = false;
  String _statusMessage = '';
  Color _statusColor = Colors.white;

  Uint8List? _imageBytes;
  String? _imageBase64;
  String? _token;

  final String apiUrl = 'https://tarabaintel.onrender.com/api/reports/';

  @override
  void initState() {
    super.initState();
    _loadToken();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() { _token = prefs.getString('jwt_token'); });
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
  }

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      Uint8List bytes = await image.readAsBytes();
      setState(() {
        _imageBytes = bytes;
        _imageBase64 = base64Encode(bytes);
      });
    }
  }

  Future<void> _submitReport() async {
    if (_descriptionController.text.isEmpty) return;
    if (_token == null) {
      _logout();
      return;
    }

    setState(() {
      _isLoading = true;
      _statusMessage = 'Sending to AI Cloud...';
      _statusColor = Colors.blue;
    });

    final payload = {
      "location": {"type": "Point", "coordinates": [11.3, 8.9]}, // Placeholder coords
      "lga": null, 
      "description": _descriptionController.text,
      "issue_category": "SECURITY",
      "image_base64": _imageBase64,
    };

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_token',
        },
        body: jsonEncode(payload),
      );

      if (response.statusCode == 201) {
        setState(() {
          _statusMessage = '✅ Report & Photo Sent! AI is analyzing...';
          _statusColor = Colors.green;
          _descriptionController.clear();
          _imageBytes = null;
          _imageBase64 = null;
        });
      } else {
        setState(() {
          _statusMessage = '❌ Server Error: ${response.statusCode}';
          _statusColor = Colors.red;
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = '❌ Network Error: $e';
        _statusColor = Colors.red;
      });
    } finally {
      setState(() { _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TarabaInsight Mobile'),
        centerTitle: true,
        actions: [
          IconButton(icon: const Icon(Icons.logout), onPressed: _logout, tooltip: 'Logout')
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Report an Incident', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            const Text('Describe what you see and attach photo evidence.', style: TextStyle(fontSize: 16, color: Colors.grey)),
            const SizedBox(height: 20),
            if (_imageBytes != null) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.memory(_imageBytes!, height: 150, width: double.infinity, fit: BoxFit.cover),
              ),
              const SizedBox(height: 10),
            ],
            OutlinedButton.icon(
              onPressed: _pickImage,
              icon: const Icon(Icons.add_photo_alternate),
              label: const Text('Attach Photo Evidence'),
              style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 15), side: const BorderSide(color: Colors.blue)),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _descriptionController,
              maxLines: 4,
              decoration: const InputDecoration(hintText: 'e.g., Armed herdsmen spotted near the river...', border: OutlineInputBorder(), filled: true),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _submitReport,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 15), backgroundColor: Colors.blue),
              child: _isLoading ? const CircularProgressIndicator(color: Colors.white) : const Text('SUBMIT REPORT', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 20),
            Text(_statusMessage, textAlign: TextAlign.center, style: TextStyle(color: _statusColor, fontSize: 16, fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}