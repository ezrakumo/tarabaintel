import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:uuid/uuid.dart';
import '../services/reward_service.dart';
import '../services/offline_db.dart';

class ReportSubmissionScreen extends StatefulWidget {
  const ReportSubmissionScreen({Key? key}) : super(key: key);

  @override
  _ReportSubmissionScreenState createState() => _ReportSubmissionScreenState();
}

class _ReportSubmissionScreenState extends State<ReportSubmissionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _descriptionController = TextEditingController();
  final _locationController = TextEditingController();
  
  String _selectedCategory = 'Security Threat';
  Uint8List? _imageBytes;
  bool _isSubmitting = false;

  final List<String> _categories = [
    'Security Threat',
    'Agricultural Crisis',
    'Public Health Issue',
    'Infrastructure Damage',
    'Environmental Hazard'
  ];

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery, 
      imageQuality: 50, // 50% quality to save bandwidth and prevent timeout
    );

    if (image != null) {
      final bytes = await image.readAsBytes();
      setState(() {
        _imageBytes = bytes;
      });
    }
  }

  Future<void> _submitReport() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSubmitting = true);
    final token = await RewardService.getToken();

    String? imageBase64;
    if (_imageBytes != null) {
      imageBase64 = base64Encode(_imageBytes!);
    }

    // ✅ 1. CHECK CONNECTIVITY
    final connectivityResult = await Connectivity().checkConnectivity();
    final isOnline = connectivityResult is List 
        ? connectivityResult.any((result) => result != ConnectivityResult.none)
        : connectivityResult != ConnectivityResult.none;

    if (isOnline) {
      // ✅ 2. ONLINE: Attempt direct API submission
      try {
        final response = await http.post(
          Uri.parse('https://tarabaintel-ai.onrender.com/api/reports/'),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({
            'description': _descriptionController.text,
            'issue_category': _selectedCategory,
            'lga_name': _locationController.text, 
            'location': 'POINT (11.3667 8.8833)', // Default Jalingo (Replace with real GPS if available)
            'image_base64': imageBase64, 
            'is_covert': false,
          }),
        ).timeout(const Duration(seconds: 30));

        if (response.statusCode == 201) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('✅ Intelligence submitted successfully!'), backgroundColor: Colors.green),
          );
          Navigator.pop(context, true); 
        } else {
          throw Exception('Server returned ${response.statusCode}');
        }
      } catch (e) {
        // 🔴 FALLBACK: If online submission fails (e.g., server timeout), save offline!
        print("⚠️ Online submission failed, falling back to offline save: $e");
        await _saveOffline(token, imageBase64);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('📴 Network unstable. Report saved offline for auto-sync.'), backgroundColor: Colors.orange),
        );
        Navigator.pop(context, true);
      }
    } else {
      // 🔴 3. OFFLINE: Save directly to local database
      print("📴 Device is offline. Saving report locally...");
      await _saveOffline(token, imageBase64);
      
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('📴 No internet. Report saved offline and will auto-sync.'),
          backgroundColor: Colors.orange,
          duration: Duration(seconds: 4),
        ),
      );
      Navigator.pop(context, true);
    }

    setState(() => _isSubmitting = false);
  }

  // ✅ HELPER: Save to local SQLite DB
  Future<void> _saveOffline(String? token, String? imageBase64) async {
    final reportId = const Uuid().v4();
    final now = DateTime.now().toIso8601String();

    final offlineReport = {
      'id': reportId,
      'category': _selectedCategory,
      'description': _descriptionController.text,
      'lga': _locationController.text,
      'lat': 8.8833, // Default Jalingo (Replace with real GPS variables if you have them)
      'lon': 11.3667,
      'image_base64': imageBase64, // Storing base64 ensures seamless syncing later
      'created_at': now,
    };

    try {
      await OfflineDb.instance.insertReport(offlineReport);
      print("💾 Successfully saved offline report: $reportId");
    } catch (e) {
      print("❌ Failed to save offline report: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Submit Intelligence'),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Issue Category', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedCategory,
                dropdownColor: const Color(0xFF1F2937),
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  filled: true, fillColor: Color(0xFF111827), border: OutlineInputBorder(),
                ),
                items: _categories.map((cat) => DropdownMenuItem(value: cat, child: Text(cat))).toList(),
                onChanged: (val) => setState(() => _selectedCategory = val!),
              ),
              const SizedBox(height: 16),

              const Text('Location / LGA', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _locationController,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'e.g., Jalingo, near the main market',
                  hintStyle: TextStyle(color: Colors.grey),
                  filled: true, fillColor: Color(0xFF111827), border: OutlineInputBorder(),
                ),
                validator: (val) => val!.isEmpty ? 'Location is required' : null,
              ),
              const SizedBox(height: 16),

              const Text('Description', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _descriptionController,
                maxLines: 5,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  hintText: 'Provide detailed intelligence...',
                  hintStyle: TextStyle(color: Colors.grey),
                  filled: true, fillColor: Color(0xFF111827), border: OutlineInputBorder(),
                ),
                validator: (val) => val!.length < 10 ? 'Description must be at least 10 characters' : null,
              ),
              const SizedBox(height: 16),

              const Text('Attach Evidence (Optional)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: _pickImage,
                child: Container(
                  height: 150,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: const Color(0xFF111827),
                    border: Border.all(color: const Color(0xFF374151), style: BorderStyle.solid),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: _imageBytes == null
                      ? const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.add_photo_alternate, color: Colors.grey, size: 40),
                            SizedBox(height: 8),
                            Text('Tap to select an image', style: TextStyle(color: Colors.grey)),
                          ],
                        )
                      : ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.memory(_imageBytes!, fit: BoxFit.cover),
                        ),
                ),
              ),
              const SizedBox(height: 24),

              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isSubmitting ? null : _submitReport,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEAB308),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  child: _isSubmitting
                      ? const CircularProgressIndicator(color: Colors.black)
                      : const Text('SUBMIT INTELLIGENCE', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 16)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}