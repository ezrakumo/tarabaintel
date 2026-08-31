import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
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
      home: const CitizenReportScreen(),
    );
  }
}

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

  // Image handling variables
  Uint8List? _imageBytes;
  String? _imageBase64;

  final String apiUrl = 'https://tarabaintel.onrender.com/api/reports/';

  // 1. Function to pick image from gallery
  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      Uint8List bytes = await image.readAsBytes();
      setState(() {
        _imageBytes = bytes;
        _imageBase64 = base64Encode(bytes); // Convert to string for API
      });
    }
  }

  // 2. Function to submit report
  Future<void> _submitReport() async {
    if (_descriptionController.text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _statusMessage = 'Sending to AI Cloud...';
      _statusColor = Colors.blue;
    });

    final payload = {
      "location": {"type": "Point", "coordinates": [11.3, 8.9]},
      "lga": null, 
      "description": _descriptionController.text,
      "issue_category": "SECURITY",
      "image_data": _imageBase64, // Send the image as Base64 text
    };

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
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
        title: const Text(' TarabaInsight Mobile'),
        centerTitle: true,
      ),
      body: SingleChildScrollView( // Added to prevent overflow when keyboard opens
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Report an Incident',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            const Text(
              'Describe what you see and attach photo evidence.',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 20),
            
            // Image Preview Area
            if (_imageBytes != null) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.memory(_imageBytes!, height: 150, width: double.infinity, fit: BoxFit.cover),
              ),
              const SizedBox(height: 10),
            ],

            // Add Photo Button
            OutlinedButton.icon(
              onPressed: _pickImage,
              icon: const Icon(Icons.add_photo_alternate),
              label: const Text('Attach Photo Evidence'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 15),
                side: const BorderSide(color: Colors.blue),
              ),
            ),
            const SizedBox(height: 20),

            // Description Text Field
            TextField(
              controller: _descriptionController,
              maxLines: 4,
              decoration: InputDecoration(
                hintText: 'e.g., Armed herdsmen spotted near the river...',
                border: const OutlineInputBorder(),
                filled: true,
              ),
            ),
            const SizedBox(height: 20),

            // Submit Button
            ElevatedButton(
              onPressed: _isLoading ? null : _submitReport,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 15),
                backgroundColor: Colors.blue,
              ),
              child: _isLoading 
                ? const CircularProgressIndicator(color: Colors.white) 
                : const Text('SUBMIT REPORT', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 20),

            // Status Message
            Text(
              _statusMessage,
              textAlign: TextAlign.center,
              style: TextStyle(color: _statusColor, fontSize: 16, fontWeight: FontWeight.w500),
            ),
          ],
        ),
      ),
    );
  }
}