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
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final token = await RewardService.getToken();
      if (token == null) {
        setState(() {
          _errorMessage = 'Authentication required. Please log in again.';
          _isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/intelligence/stakeholder-dashboard/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 30)); // ✅ Prevents infinite hanging

      if (response.statusCode == 200) {
        setState(() {
          _dashboardData = jsonDecode(response.body);
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = 'Server error: ${response.statusCode}';
          _isLoading = false; // ✅ Crucial: Stops the infinite loader!
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Network error: $e';
        _isLoading = false; // ✅ Crucial: Stops the infinite loader!
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Intelligence Command Center', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboard,
            tooltip: 'Refresh Intelligence',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFEAB308)))
          : _errorMessage != null
              ? _buildErrorView()
              : _dashboardData == null
                  ? const Center(child: Text('No data available', style: TextStyle(color: Colors.white)))
                  : _buildDashboard(),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.redAccent),
          const SizedBox(height: 16),
          Text(_errorMessage!, style: const TextStyle(color: Colors.white, fontSize: 16)),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadDashboard,
            icon: const Icon(Icons.refresh),
            label: const Text('Retry Connection'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEAB308),
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboard() {
    final kpis = _dashboardData!['kpis'];
    final topThreats = _dashboardData!['top_threats'] as List<dynamic>;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Real-Time Intelligence Overview',
            style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'Last updated: ${_dashboardData!['generated_at']}',
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          const SizedBox(height: 24),

          // KPI Grid - Row 1
          Row(
            children: [
              Expanded(child: _buildKPICard('Reports (24h)', '${kpis['reports_24h']}', Icons.report, Colors.blue)),
              const SizedBox(width: 12),
              Expanded(child: _buildKPICard('Critical Active', '${kpis['critical_active']}', Icons.warning, Colors.red)),
            ],
          ),
          const SizedBox(height: 12),

          // KPI Grid - Row 2
          Row(
            children: [
              Expanded(child: _buildKPICard('Pending Verification', '${kpis['pending_verifications']}', Icons.task, Colors.orange)),
              const SizedBox(width: 12),
              Expanded(child: _buildKPICard('Active Agents', '${kpis['active_agents']}', Icons.people, Colors.green)),
            ],
          ),
          const SizedBox(height: 32),

          // Active Threats Section
          const Text(
            '🚨 Active Threats Requiring Attention',
            style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          topThreats.isEmpty
              ? Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1F2937),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Center(
                    child: Text('No active threats at this time. All clear.', style: TextStyle(color: Colors.grey, fontSize: 14)),
                  ),
                )
              : Column(
                  children: topThreats.map((threat) => _buildThreatCard(threat)).toList(),
                ),
        ],
      ),
    );
  }

  Widget _buildKPICard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 12), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  Widget _buildThreatCard(Map<String, dynamic> threat) {
    final isCritical = threat['urgency'] == 'CRITICAL';
    final color = isCritical ? Colors.red : Colors.orange;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 2),
      ),
      child: Row(
        children: [
          Icon(isCritical ? Icons.error : Icons.warning, color: color, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(threat['category'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 4),
                Text('${threat['location']} • ${threat['urgency']}', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                const SizedBox(height: 4),
                Text('Confidence: ${(threat['confidence'] * 100).toInt()}%', style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          const Icon(Icons.chevron_right, color: Colors.white54),
        ],
      ),
    );
  }
}