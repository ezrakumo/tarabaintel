import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/reward_service.dart';

class StakeholderDashboardScreen extends StatefulWidget {
  const StakeholderDashboardScreen({Key? key}) : super(key: key);

  @override
  _StakeholderDashboardScreenState createState() => _StakeholderDashboardScreenState();
}

class _StakeholderDashboardScreenState extends State<StakeholderDashboardScreen> {
  Map<String, dynamic>? _dashboardData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() => _isLoading = true);
    
    final token = await RewardService.getToken();
    final response = await http.get(
      Uri.parse('https://tarabaintel-ai.onrender.com/api/intelligence/stakeholder-dashboard/'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      setState(() {
        _dashboardData = jsonDecode(response.body);
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Intelligence Command Center'),
        backgroundColor: const Color(0xFF1F2937),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboard,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFEAB308)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // KPI Cards
                  Row(
                    children: [
                      Expanded(child: _buildKPICard('Reports (24h)', '${_dashboardData!['kpis']['reports_24h']}', Icons.report)),
                      const SizedBox(width: 12),
                      Expanded(child: _buildKPICard('Critical', '${_dashboardData!['kpis']['critical_active']}', Icons.warning, color: Colors.red)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: _buildKPICard('Pending Verification', '${_dashboardData!['kpis']['pending_verifications']}', Icons.task)),
                      const SizedBox(width: 12),
                      Expanded(child: _buildKPICard('Active Agents', '${_dashboardData!['kpis']['active_agents']}', Icons.people)),
                    ],
                  ),
                  const SizedBox(height: 24),
                  
                  // Top Threats
                  const Text('Active Threats Requiring Attention', 
                    style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  ...(_dashboardData!['top_threats'] as List).map((threat) => _buildThreatCard(threat)),
                ],
              ),
            ),
    );
  }

  Widget _buildKPICard(String title, String value, IconData icon, {Color? color}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color ?? const Color(0xFFEAB308), size: 32),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildThreatCard(Map<String, dynamic> threat) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: threat['urgency'] == 'CRITICAL' 
            ? Colors.red.withOpacity(0.2) 
            : Colors.orange.withOpacity(0.2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: threat['urgency'] == 'CRITICAL' ? Colors.red : Colors.orange,
        ),
      ),
      child: Row(
        children: [
          Icon(
            threat['urgency'] == 'CRITICAL' ? Icons.error : Icons.warning,
            color: threat['urgency'] == 'CRITICAL' ? Colors.red : Colors.orange,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(threat['category'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                Text('${threat['location']} • ${threat['urgency']}', 
                  style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
          Text('${(threat['confidence'] * 100).toInt()}%', 
            style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }
}