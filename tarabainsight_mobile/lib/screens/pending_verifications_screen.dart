import 'package:flutter/material.dart';
import '../services/verification_service.dart';
import 'verification_action_screen.dart';

class PendingVerificationsScreen extends StatefulWidget {
  const PendingVerificationsScreen({Key? key}) : super(key: key);

  @override
  _PendingVerificationsScreenState createState() => _PendingVerificationsScreenState();
}

class _PendingVerificationsScreenState extends State<PendingVerificationsScreen> {
  List<dynamic> _tasks = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  Future<void> _loadTasks() async {
    setState(() { 
      _isLoading = true; 
      _errorMessage = null; 
    });
    
    try {
      // ✅ responseData is now dynamic, so we can safely check its type
      final responseData = await VerificationService.getPendingVerifications();
      
      List<dynamic> taskList = [];
      
      if (responseData is List) {
        // Backend returned a direct list: [...]
        taskList = responseData;
      } else if (responseData is Map) {
        // Backend returned a paginated object: {"count": 1, "results": [...]}
        if (responseData.containsKey('results') && responseData['results'] is List) {
          taskList = responseData['results'];
        } else {
          // Fallback: treat the whole map as a single task
          taskList = [responseData]; 
        }
      }
      
      setState(() {
        _tasks = taskList;
        _isLoading = false;
      });
      
      print("✅ Loaded ${_tasks.length} pending verifications");
    } catch (e) {
      print("❌ Error loading verifications: $e");
      setState(() {
        _errorMessage = 'Failed to load verifications: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Pending Verifications'),
        backgroundColor: const Color(0xFF1F2937),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadTasks),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.amber))
          : _errorMessage != null
              ? Center(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)))
              : _tasks.isEmpty
                  ? const Center(
                      child: Text('🎉 All clear! No pending verifications.', 
                      style: TextStyle(color: Colors.white, fontSize: 16)),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _tasks.length,
                      itemBuilder: (context, index) {
                        final task = _tasks[index];
                        final report = task['report'] ?? {};
                        return Card(
                          color: const Color(0xFF1F2937),
                          margin: const EdgeInsets.only(bottom: 16),
                          child: ListTile(
                            leading: const Icon(Icons.assignment_turned_in, color: Colors.amber, size: 40),
                            title: Text(report['issue_category'] ?? 'Unknown Category', 
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 4),
                                Text('LGA: ${report['lga_name'] ?? 'Unknown'}', style: const TextStyle(color: Colors.grey)),
                                Text(report['description'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.grey)),
                              ],
                            ),
                            trailing: const Icon(Icons.arrow_forward_ios, color: Colors.grey, size: 16),
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => VerificationActionScreen(
                                    verificationId: task['id'].toString(),
                                    reportData: report,
                                    onSuccess: _loadTasks, // Refresh list after completion
                                  ),
                                ),
                              );
                            },
                          ),
                        );
                      },
                    ),
    );
  }
}