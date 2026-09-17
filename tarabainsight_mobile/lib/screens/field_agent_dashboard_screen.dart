import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/reward_service.dart';
import 'command_center_screen.dart'; // ✅ Adds the new screen

class FieldAgentDashboardScreen extends StatefulWidget {
  const FieldAgentDashboardScreen({Key? key}) : super(key: key);

  @override
  _FieldAgentDashboardScreenState createState() => _FieldAgentDashboardScreenState();
}

class _FieldAgentDashboardScreenState extends State<FieldAgentDashboardScreen> {
  List<dynamic> _pendingVerifications = [];
  bool _isLoading = true;
  String _agentId = 'AGENT-001';

  @override
  void initState() {
    super.initState();
    _loadPendingVerifications();
  }

  Future<void> _loadPendingVerifications() async {
    setState(() => _isLoading = true);
    final token = await RewardService.getToken();
    
    try {
      final response = await http.get(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/field-verifications/'),
        headers: {'Authorization': 'Bearer $token'},
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        List<dynamic> verificationsList = [];
        
        if (data is List) {
          verificationsList = data;
        } else if (data is Map && data.containsKey('results')) {
          verificationsList = data['results'];
        }

        setState(() {
          _pendingVerifications = verificationsList.where((v) => 
            v['status'] == 'PENDING' || v['status'] == 'ASSIGNED'
          ).toList();
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      setState(() => _isLoading = false);
      print("Error: $e");
    }
  }

  Future<void> _claimVerification(String verificationId) async {
    final token = await RewardService.getToken();
    try {
      final response = await http.post(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/field-verifications/$verificationId/claim/'),
        headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
        body: jsonEncode({'agent_id': _agentId}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Claimed!'), backgroundColor: Colors.green),
        );
        _loadPendingVerifications();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: ${response.body}'), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _completeVerification(String verificationId, bool isValid, String notes) async {
    final token = await RewardService.getToken();
    try {
      final response = await http.post(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/field-verifications/$verificationId/complete/'),
        headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
        body: jsonEncode({'agent_id': _agentId, 'is_valid': isValid, 'notes': notes}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Verified!'), backgroundColor: Colors.green),
        );
        _loadPendingVerifications();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: ${response.body}'), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    }
  }

  void _showCompleteDialog(String verificationId, String reportDesc) {
    final notesController = TextEditingController();
    bool isValid = true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          backgroundColor: const Color(0xFF1F2937),
          title: const Text('Verify Report', style: TextStyle(color: Colors.white)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Report: $reportDesc', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                const SizedBox(height: 16),
                const Text('Is this valid?', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                Row(
                  children: [
                    Expanded(child: RadioListTile<bool>(title: const Text('✅ Valid', style: TextStyle(color: Colors.green)), value: true, groupValue: isValid, onChanged: (val) => setDialogState(() => isValid = val!))),
                    Expanded(child: RadioListTile<bool>(title: const Text('❌ Invalid', style: TextStyle(color: Colors.red)), value: false, groupValue: isValid, onChanged: (val) => setDialogState(() => isValid = val!))),
                  ],
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: notesController,
                  maxLines: 3,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(hintText: 'Notes...', hintStyle: TextStyle(color: Colors.grey), filled: true, fillColor: Color(0xFF111827), border: OutlineInputBorder()),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel', style: TextStyle(color: Colors.grey))),
            ElevatedButton(
              onPressed: () { Navigator.pop(context); _completeVerification(verificationId, isValid, notesController.text); },
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFEAB308)),
              child: const Text('SUBMIT', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Field Agent Dashboard'),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
        actions: [
    // ✅ ADD THIS BUTTON TO OPEN THE COMMAND CENTER
            IconButton(
                icon: const Icon(Icons.map, color: Colors.green, size: 28),
                tooltip: 'Open Real-Time Command Center',
                onPressed: () {
                    Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const CommandCenterScreen()),
        );
      },
    ),
    const SizedBox(width: 8), // Adds a little spacing
  ],
),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFEAB308)))
          : _pendingVerifications.isEmpty
              ? const Center(child: Text('🎉 No pending verifications.', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey, fontSize: 16)))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _pendingVerifications.length,
                  itemBuilder: (context, index) {
                    final v = _pendingVerifications[index];
                    final report = (v['report'] is Map) ? v['report'] : {};
                    
                    // ✅ CORRECTED DATA EXTRACTION
                    final category = report['issue_category']?.toString() ?? 'Unknown Category';
                    final description = report['description']?.toString() ?? 'No description';
                    final location = report['lga_name']?.toString() ?? report['location']?.toString() ?? 'Unknown Location';
                    final status = v['status']?.toString() ?? 'PENDING';
                    
                    // ✅ CORRECTED AGENT CHECK (Matches the new backend string format)
                    final assignedAgentId = v['assigned_agent_id']?.toString();
                    final isClaimed = status == 'ASSIGNED' && assignedAgentId == _agentId;
                    final verificationId = v['id']?.toString() ?? '';

                    return Card(
                      color: const Color(0xFF1F2937),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Color(0xFF374151))),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(isClaimed ? '🔒 CLAIMED' : '📡 PENDING', style: TextStyle(color: isClaimed ? Colors.green : Colors.orange, fontWeight: FontWeight.bold)),
                                const Text('Just now', style: TextStyle(color: Colors.grey, fontSize: 12)),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(category, style: const TextStyle(color: Color(0xFFEAB308), fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 4),
                            Text(description, style: const TextStyle(color: Colors.white, fontSize: 14)),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                const Icon(Icons.location_on, color: Colors.grey, size: 16),
                                const SizedBox(width: 4),
                                Text(location, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                              ],
                            ),
                            const SizedBox(height: 16),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: verificationId.isNotEmpty ? (isClaimed ? () => _showCompleteDialog(verificationId, description) : () => _claimVerification(verificationId)) : null,
                                style: ElevatedButton.styleFrom(backgroundColor: isClaimed ? Colors.green : const Color(0xFFEAB308), foregroundColor: Colors.black, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
                                child: Text(isClaimed ? 'COMPLETE VERIFICATION' : 'CLAIM REPORT', style: const TextStyle(fontWeight: FontWeight.bold)),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}