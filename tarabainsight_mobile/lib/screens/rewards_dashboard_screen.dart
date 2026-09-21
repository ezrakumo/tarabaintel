import 'package:flutter/material.dart';
import '../models/reward_models.dart';
import '../services/reward_service.dart';
import 'report_submission_screen.dart';
import 'pending_verifications_screen.dart';
import 'command_center_screen.dart';

class RewardsDashboardScreen extends StatefulWidget {
  const RewardsDashboardScreen({Key? key}) : super(key: key);

  @override
  _RewardsDashboardScreenState createState() => _RewardsDashboardScreenState();
}

class _RewardsDashboardScreenState extends State<RewardsDashboardScreen> {
  DashboardResponse? _dashboard;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final dashboard = await RewardService.getDashboard();

    if (mounted) {
      setState(() {
        _dashboard = dashboard;
        _isLoading = false;
      });
    }
  }

  Future<void> _redeemReward(Reward reward) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1F2937),
        title: const Text('Confirm Redemption', style: TextStyle(color: Colors.white)),
        content: Text(
          'Redeem "${reward.title}" for ${reward.pointsRequired} points?',
          style: const TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFEAB308)),
            child: const Text('Confirm', style: TextStyle(color: Colors.black)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final result = await RewardService.redeemReward(reward.id);
      
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result?['message'] ?? 'Redeemed successfully!'),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 3),
        ),
      );
      
      _loadData(); // Refresh data to show updated points
      
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFF0A0E17),
        body: Center(child: CircularProgressIndicator(color: Color(0xFFEAB308))),
      );
    }

    if (_dashboard == null) {
      return Scaffold(
        backgroundColor: const Color(0xFF0A0E17),
        appBar: AppBar(
          title: const Text('My Rewards'),
          backgroundColor: const Color(0xFF1F2937),
          elevation: 0,
        ),
        body: const Center(
          child: Text('Failed to load dashboard. Please login again.', style: TextStyle(color: Colors.white)),
        ),
      );
    }

    // ✅ USE FLAT STRUCTURE (NO NESTED PROFILE)
    final totalPoints = _dashboard!.totalPoints;
    final userTier = _dashboard!.userTier;
    final pointsToNext = _dashboard!.pointsToNextTier;
    final nextTier = _dashboard!.nextTier;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('My Rewards'),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
        actions: [
          // ✅ 1. RED SUBMIT REPORT ICON
          IconButton(
            icon: const Icon(Icons.post_add, color: Colors.redAccent),
            tooltip: 'Submit New Report',
            onPressed: () async {
              final result = await Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ReportSubmissionScreen()),
              );
              if (result == true) {
                _loadData();
              }
            },
          ),

          // ✅ 2. AMBER PENDING VERIFICATIONS ICON
          IconButton(
            icon: const Icon(Icons.task_alt, color: Colors.amber),
            tooltip: 'Pending Verifications',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const PendingVerificationsScreen()),
              );
            },
          ),

          // ✅ 3. BLUE COMMAND CENTER MAP ICON
          IconButton(
            icon: const Icon(Icons.map, color: Colors.blue),
            tooltip: 'Command Center Map',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CommandCenterScreen()),
              );
            },
          ),

          // ✅ 4. WHITE REFRESH ICON
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Data',
            onPressed: () {
              _loadData(); 
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Points & Tier Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFFEAB308), Color(0xFFCA8A04)]),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Available Points', style: TextStyle(color: Colors.white70, fontSize: 16)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          userTier, // ✅ USE FLAT userTier
                          style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('$totalPoints', style: const TextStyle(color: Colors.white, fontSize: 48, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  LinearProgressIndicator(
                    value: pointsToNext > 0 
                        ? (totalPoints / (totalPoints + pointsToNext)).clamp(0.0, 1.0)
                        : 1.0,
                    backgroundColor: Colors.white24,
                    valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                    minHeight: 8,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$pointsToNext pts to ${nextTier ?? 'MAX TIER'}',
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 2. Affordable Rewards Section
            const Text('Affordable Rewards', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _dashboard!.affordableRewards.isEmpty
                ? Container(
                    padding: const EdgeInsets.all(20),
                    width: double.infinity,
                    decoration: BoxDecoration(color: const Color(0xFF1F2937), borderRadius: BorderRadius.circular(12)),
                    child: const Text('No rewards available yet. Earn more points!', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey)),
                  )
                : SizedBox(
                    height: 260,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _dashboard!.affordableRewards.length,
                      itemBuilder: (context, index) {
                        final reward = _dashboard!.affordableRewards[index];
                        return Container(
                          width: 220,
                          margin: const EdgeInsets.only(right: 12),
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1F2937),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFF374151)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(reward.title, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                              const SizedBox(height: 8),
                              Text(reward.description ?? 'No description', style: const TextStyle(color: Colors.grey, fontSize: 12), maxLines: 2, overflow: TextOverflow.ellipsis),
                              const Spacer(),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text('${reward.pointsRequired} pts', style: const TextStyle(color: Color(0xFFFCD34D), fontWeight: FontWeight.bold)),
                                  const Icon(Icons.card_giftcard, color: Color(0xFFFCD34D)),
                                ],
                              ),
                              const SizedBox(height: 12),
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton(
                                  onPressed: () => _redeemReward(reward),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFFEAB308),
                                    foregroundColor: Colors.black,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                    padding: const EdgeInsets.symmetric(vertical: 8),
                                  ),
                                  child: const Text('REDEEM', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                ),
                              )
                            ],
                          ),
                        );
                      },
                    ),
                  ),
            const SizedBox(height: 24),

            // 3. Recent Transactions
            const Text('Recent Activity', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _dashboard!.recentTransactions.isEmpty
                ? const Text('No recent activity.', style: TextStyle(color: Colors.grey))
                : Column(
                    children: _dashboard!.recentTransactions.map((tx) => Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1F2937),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(tx.points > 0 ? Icons.add_circle : Icons.remove_circle, color: tx.points > 0 ? Colors.green : Colors.red),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(tx.description, style: const TextStyle(color: Colors.white, fontSize: 14)),
                              ],
                            ),
                          ),
                          Text('${tx.points > 0 ? '+' : ''}${tx.points}', style: TextStyle(color: tx.points > 0 ? Colors.green : Colors.red, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    )).toList(),
                  ),
          ],
        ),
      ),
    );
  }
}