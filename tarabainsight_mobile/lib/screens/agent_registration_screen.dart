import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AgentRegistrationScreen extends StatefulWidget {
  const AgentRegistrationScreen({Key? key}) : super(key: key);

  @override
  _AgentRegistrationScreenState createState() => _AgentRegistrationScreenState();
}

class _AgentRegistrationScreenState extends State<AgentRegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _lgaController = TextEditingController();
  final _reasonController = TextEditingController();
  
  bool _isLoading = false;

  Future<void> _submitRegistration() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/agents/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'full_name': _fullNameController.text.trim(),
          'phone_number': _phoneController.text.trim(),
          'email': _emailController.text.trim(),
          'lga': _lgaController.text.trim(),
          'reason_for_joining': _reasonController.text.trim(),
        }),
      );

      if (response.statusCode == 201) {
        // Success!
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            backgroundColor: const Color(0xFF1F2937),
            title: const Text('✅ Application Submitted!', style: TextStyle(color: Colors.white)),
            content: const Text(
              'Your application has been received. The Command will review your details and contact you upon approval.',
              style: TextStyle(color: Colors.grey),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context); // Close dialog
                  Navigator.pop(context); // Go back to login
                },
                child: const Text('OK', style: TextStyle(color: Color(0xFFEAB308))),
              ),
            ],
          ),
        );
      } else {
        final data = jsonDecode(response.body);
        String errorMsg = 'Registration failed. Please try again.';
        if (data['phone_number'] != null) {
          errorMsg = 'This phone number is already registered.';
        }
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(errorMsg), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Network error: $e'), backgroundColor: Colors.red),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Agent Application'),
        backgroundColor: const Color(0xFF1F2937),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Join TarabaInsight Field Network',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Help secure Taraba State. Submit your application below.',
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 32),

              _buildTextField(_fullNameController, 'Full Name', false),
              const SizedBox(height: 16),

              _buildTextField(_phoneController, 'Phone Number', false, TextInputType.phone),
              const SizedBox(height: 16),

              _buildTextField(_emailController, 'Email Address', true, TextInputType.emailAddress),
              const SizedBox(height: 16),

              _buildTextField(_lgaController, 'Local Government Area (LGA)', false),
              const SizedBox(height: 16),

              TextFormField(
                controller: _reasonController,
                maxLines: 4,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  labelText: 'Why do you want to join?',
                  labelStyle: TextStyle(color: Colors.grey),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.grey)),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFFEAB308))),
                  filled: true,
                  fillColor: Color(0xFF1F2937),
                ),
                validator: (value) => value!.isEmpty ? 'Please tell us your motivation' : null,
              ),
              const SizedBox(height: 32),

              ElevatedButton(
                onPressed: _isLoading ? null : _submitRegistration,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFEAB308),
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.black)
                    : const Text('SUBMIT APPLICATION', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String label, bool isOptional, [TextInputType? keyboardType]) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: isOptional ? '$label (Optional)' : label,
        labelStyle: const TextStyle(color: Colors.grey),
        enabledBorder: const OutlineInputBorder(borderSide: BorderSide(color: Colors.grey)),
        focusedBorder: const OutlineInputBorder(borderSide: BorderSide(color: Color(0xFFEAB308))),
        filled: true,
        fillColor: const Color(0xFF1F2937),
      ),
      validator: (value) {
        if (!isOptional && (value == null || value.isEmpty)) {
          return '$label is required';
        }
        return null;
      },
    );
  }
}