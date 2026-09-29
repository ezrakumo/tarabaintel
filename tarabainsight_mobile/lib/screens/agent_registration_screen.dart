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
  final _notesController = TextEditingController();
  
  bool _isLoading = false;

  // ✅ DYNAMIC DROPDOWN DATA
  final List<String> _states = ['Taraba State', 'Delta State'];
  final Map<String, List<String>> _lgas = {
    'Taraba State': [
      'Jalingo', 'Wukari', 'Gembu', 'Bali', 'Takum', 'Ibi', 'Sardauna', 
      'Karim Lamido', 'Zing', 'Yorro', 'Ardo Kola', 'Donga', 'Gashaka', 
      'Ila', 'Kurmi', 'Lau', 'Ussa'
    ],
    'Delta State': [
      'Asaba', 'Warri', 'Sapele', 'Ughelli', 'Agbor', 'Kwale', 'Ogwashi-Uku', 
      'Abraka', 'Koko', 'Isoko', 'Ozoro', 'Patani', 'Burutu', 'Bomadi', 
      'Effurun', 'Ukwuani', 'Akuku', 'Onicha-Ugbo', 'Idumuje-Ugboko', 
      'Abbi', 'Ogor', 'Ogidigben', 'Otor-Udu', 'Udu', 'Orerokpe'
    ],
  };
  
  final List<String> _reasons = [
    'Community Security & Safety',
    'Financial Incentives & Rewards',
    'Patriotism & National Service',
    'Career in Intelligence & Security',
    'Other (Please specify in notes)'
  ];

  String _selectedState = 'Taraba State';
  String? _selectedLga;
  String _selectedReason = 'Community Security & Safety';

  @override
  void initState() {
    super.initState();
    // ✅ Set default LGA based on default state
    _selectedLga = _lgas[_selectedState]!.first;
  }

  Future<void> _submitRegistration() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      // ✅ FORMAT THE REASON TO INCLUDE STATE AND NOTES (No backend changes needed!)
      String formattedReason = 'State: $_selectedState\nPrimary Reason: $_selectedReason';
      if (_notesController.text.trim().isNotEmpty) {
        formattedReason += '\nAdditional Notes: ${_notesController.text.trim()}';
      }

      final response = await http.post(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/agents/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'full_name': _fullNameController.text.trim(),
          'phone_number': _phoneController.text.trim(),
          'email': _emailController.text.trim(),
          'lga': _selectedLga,
          'reason_for_joining': formattedReason,
        }),
      );

      if (response.statusCode == 201) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            backgroundColor: const Color(0xFF1F2937),
            title: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green, size: 28),
                SizedBox(width: 10),
                Text('Application Submitted!', style: TextStyle(color: Colors.white)),
              ],
            ),
            content: const Text(
              'Your application has been received. The NigeriaInsight Command will review your details and contact you upon approval.',
              style: TextStyle(color: Colors.grey),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context); // Close dialog
                  Navigator.pop(context); // Go back to login
                },
                child: const Text('RETURN TO LOGIN', style: TextStyle(color: Color(0xFFEAB308), fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        );
      } else {
        final data = jsonDecode(response.body);
        String errorMsg = 'Registration failed. Please try again.';
        if (data['phone_number'] != null) {
          errorMsg = 'This phone number is already registered.';
        } else if (data is Map && data.containsKey('error')) {
          errorMsg = data['error'].toString();
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
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Agent Application'),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Join NigeriaInsight Field Network',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Help secure our nation. Submit your application below.',
                style: TextStyle(color: Colors.grey, fontSize: 15),
              ),
              const SizedBox(height: 32),

              _buildTextField(_fullNameController, 'Full Name', false),
              const SizedBox(height: 16),

              _buildTextField(_phoneController, 'Phone Number', false, TextInputType.phone),
              const SizedBox(height: 16),

              _buildTextField(_emailController, 'Email Address', true, TextInputType.emailAddress),
              const SizedBox(height: 16),

              // ✅ STATE DROPDOWN
              _buildDropdown('State of Operation', _selectedState, _states, (newValue) {
                setState(() {
                  _selectedState = newValue!;
                  _selectedLga = _lgas[_selectedState]!.first; // Reset LGA when state changes
                });
              }),
              const SizedBox(height: 16),

              // ✅ DYNAMIC LGA DROPDOWN
              _buildDropdown('Local Government Area (LGA)', _selectedLga!, _lgas[_selectedState]!, (newValue) {
                setState(() {
                  _selectedLga = newValue;
                });
              }),
              const SizedBox(height: 16),

              // ✅ REASON DROPDOWN
              _buildDropdown('Primary Reason for Joining', _selectedReason, _reasons, (newValue) {
                setState(() {
                  _selectedReason = newValue!;
                });
              }),
              const SizedBox(height: 16),

              // ✅ ADDITIONAL NOTES FIELD
              TextFormField(
                controller: _notesController,
                maxLines: 4,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  labelText: 'Additional Notes (Optional)',
                  hintText: 'e.g., Specific local knowledge, languages spoken, etc.',
                  hintStyle: TextStyle(color: Colors.grey, fontSize: 13),
                  labelStyle: TextStyle(color: Colors.grey),
                  enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.grey)),
                  focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Color(0xFFEAB308))),
                  filled: true,
                  fillColor: Color(0xFF1F2937),
                ),
              ),
              const SizedBox(height: 32),

              ElevatedButton(
                onPressed: _isLoading ? null : _submitRegistration,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFEAB308),
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 4,
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.black)
                    : const Text('SUBMIT APPLICATION', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  // ✅ REUSABLE DROPDOWN WIDGET
  Widget _buildDropdown(String label, String value, List<String> items, ValueChanged<String?> onChanged) {
    return DropdownButtonFormField<String>(
      value: value,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.grey),
        enabledBorder: const OutlineInputBorder(borderSide: BorderSide(color: Colors.grey)),
        focusedBorder: const OutlineInputBorder(borderSide: BorderSide(color: Color(0xFFEAB308))),
        filled: true,
        fillColor: const Color(0xFF1F2937),
      ),
      dropdownColor: const Color(0xFF1F2937),
      icon: const Icon(Icons.arrow_drop_down, color: Colors.grey),
      items: items.map((item) => DropdownMenuItem(
        value: item,
        child: Text(item, style: const TextStyle(color: Colors.white)),
      )).toList(),
      onChanged: onChanged,
      validator: (value) => value == null || value.isEmpty ? 'Please select a $label' : null,
    );
  }

  // ✅ REUSABLE TEXT FIELD WIDGET
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