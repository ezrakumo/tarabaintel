import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

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
        brightness: Brightness.dark, // Cool dark theme like our dashboard
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
  bool _isLoading = false;
  String _statusMessage = '';
  Color _statusColor = Colors.white;

  // THE CLOUD API ENDPOINT
  final String apiUrl = 'https://tarabaintel.onrender.com/api/reports/';

  Future<void> _submitReport() async {
    if (_descriptionController.text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _statusMessage = 'Sending to AI Cloud...';
      _statusColor = Colors.blue;
    });

    // Hardcoded coordinates for testing (Jalingo area)
    final payload = {
      "location": {"type": "Point", "coordinates": [11.3, 8.9]},
      "lga": null, 
      "description": _descriptionController.text,
      "issue_category": "SECURITY"
    };

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 201) {
        setState(() {
          _statusMessage = '✅ Report Sent! AI is analyzing...';
          _statusColor = Colors.green;
          _descriptionController.clear();
        });
      } else {
        setState(() {
          _statusMessage = '❌ Failed: ${response.statusCode}';
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
        title: const Text('️ TarabaInsight Mobile'),
        centerTitle: true,
      ),
      body: Padding(
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
              'Describe what you see. Our AI will analyze the threat level instantly.',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 30),
            TextField(
              controller: _descriptionController,
              maxLines: 5,
              decoration: InputDecoration(
                hintText: 'e.g., Armed herdsmen spotted near the river...',
                border: const OutlineInputBorder(),
                filled: true,
              ),
            ),
            const SizedBox(height: 20),
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