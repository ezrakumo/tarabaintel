import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:typed_data';
import '../services/verification_service.dart';

class VerificationActionScreen extends StatefulWidget {
  final String verificationId;
  final Map<String, dynamic> reportData;
  final VoidCallback onSuccess;

  const VerificationActionScreen({
    Key? key, 
    required this.verificationId, 
    required this.reportData, 
    required this.onSuccess,
  }) : super(key: key);

  @override
  _VerificationActionScreenState createState() => _VerificationActionScreenState();
}

class _VerificationActionScreenState extends State<VerificationActionScreen> {
  final _notesController = TextEditingController();
  Uint8List? _verificationImage;
  bool _isValid = true;
  bool _isSubmitting = false;
  bool _isClaimed = false;

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.camera, imageQuality: 60);
    if (image != null) {
      setState(() {
        _verificationImage = null; // Clear first to show loading if needed
      });
      final bytes = await image.readAsBytes();
      setState(() {
        _verificationImage = bytes;
      });
    }
  }

  Future<void> _claimAndComplete() async {
    setState(() => _isSubmitting = true);

    try {
      // 1. Claim the task first
      if (!_isClaimed) {
        await VerificationService.claimVerification(widget.verificationId);
        setState(() => _isClaimed = true);
      }

      // 2. Complete the task
      String? imageBase64;
      if (_verificationImage != null) {
        imageBase64 = base64Encode(_verificationImage!);
      }

      await VerificationService.completeVerification(
        widget.verificationId,
        _isValid,
        _notesController.text,
        imageBase64,
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('✅ Verification submitted successfully!'), backgroundColor: Colors.green),
      );
      
      widget.onSuccess(); // Refresh parent list
      Navigator.pop(context); // Go back
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Verify Report'),
        backgroundColor: const Color(0xFF1F2937),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Original Report Details
            const Text('ORIGINAL REPORT', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Card(
              color: const Color(0xFF111827),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Category: ${widget.reportData['issue_category']}', style: const TextStyle(color: Colors.white)),
                    const SizedBox(height: 8),
                    Text('Location: ${widget.reportData['lga_name']}', style: const TextStyle(color: Colors.white)),
                    const SizedBox(height: 8),
                    Text(widget.reportData['description'] ?? 'No description', style: const TextStyle(color: Colors.grey)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Verification Findings
            const Text('YOUR VERIFICATION', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            
            // Valid/Invalid Toggle
            Row(
              children: [
                Expanded(
                  child: ChoiceChip(
                    label: const Text('✅ Valid / Confirmed'),
                    selected: _isValid,
                    onSelected: (val) => setState(() => _isValid = true),
                    selectedColor: Colors.green,
                    backgroundColor: const Color(0xFF1F2937),
                    labelStyle: TextStyle(color: _isValid ? Colors.black : Colors.white),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ChoiceChip(
                    label: const Text('❌ Invalid / False Alarm'),
                    selected: !_isValid,
                    onSelected: (val) => setState(() => _isValid = false),
                    selectedColor: Colors.red,
                    backgroundColor: const Color(0xFF1F2937),
                    labelStyle: TextStyle(color: !_isValid ? Colors.black : Colors.white),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Notes
            TextFormField(
              controller: _notesController,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                hintText: 'Add field notes (e.g., "Visited location, no threat found")',
                hintStyle: TextStyle(color: Colors.grey),
                filled: true, fillColor: Color(0xFF111827), border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),

            // Camera Button
            GestureDetector(
              onTap: _pickImage,
              child: Container(
                height: 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: const Color(0xFF111827),
                  border: Border.all(color: const Color(0xFF374151)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: _verificationImage == null
                    ? const Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.camera_alt, color: Colors.grey, size: 40),
                          SizedBox(height: 8),
                          Text('Tap to take verification photo', style: TextStyle(color: Colors.grey)),
                        ],
                      )
                    : ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.memory(_verificationImage!, fit: BoxFit.cover),
                      ),
              ),
            ),
            const SizedBox(height: 32),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _claimAndComplete,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFEAB308),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.black)
                    : const Text('SUBMIT VERIFICATION', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}