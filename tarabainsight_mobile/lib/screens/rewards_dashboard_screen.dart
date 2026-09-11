import 'package:flutter/material.dart';
import '../../models/reward_models.dart';
import '../../services/reward_service.dart';

class RewardsDashboardScreen extends StatefulWidget {
  final String authToken;
  const RewardsDashboardScreen({Key? key, required this.authToken}) : super(key: key);

  @override
  _RewardsDashboardScreenState createState() => _RewardsDashboardScreenState();
}

class _RewardsDashboardScreenState extends State<RewardsDashboardScreen> {
  UserProfile? _profile;
  List<Reward> _rewards = [];
  List<LedgerEntry> _ledger = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final profile = await RewardService.getProfile(widget.authToken);
    final rewards = await RewardService.getCatalog(widget.authToken);
    final ledger = await RewardService.getLedger(widget.authToken);

    setState(() {
      _profile = profile;
      _rewards = rewards;
      _ledger = ledger;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      backgroundColor: Color(0xFF0A0E17), // Dark background
      appBar: AppBar(
        title: Text('My Rewards'),
        backgroundColor: Color(0xFF1F2937),
        elevation: 0,
      ),
      body: _profile == null
          ? Center(child: Text('Failed to load profile', style: TextStyle(color: Colors.white)))
          : SingleChildScrollView(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Points Card
                  Container(
                    padding: EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(colors: [Color(0xFFEAB308), Color(0xFFCA8A04)]),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Available Points', style: TextStyle(color: Colors.white70, fontSize: 16)),
                        SizedBox(height: 8),
                        Text('${_profile!.totalPoints}', style: TextStyle(color: Colors.white, fontSize: 48, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        Text('Tier: ${_profile!.tier}', style: TextStyle(color: Colors.white, fontSize: 16)),
                      ],
                    ),
                  ),
                  SizedBox(height: 24),

                  // Available Rewards
                  Text('Available Rewards', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                  SizedBox(height: 12),
                  ..._rewards.map((reward) => _buildRewardCard(reward)),
                  SizedBox(height: 24),

                  // Recent Transactions
                  Text('Recent Transactions', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                  SizedBox(height: 12),
                  ..._ledger.take(5).map((entry) => _buildLedgerCard(entry)),
                ],
              ),
            ),
    );
  }

  Widget _buildRewardCard(Reward reward) {
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Color(0xFF374151)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(reward.title, style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                SizedBox(height: 4),
                Text(reward.description, style: TextStyle(color: Colors.grey, fontSize: 12), maxLines: 2, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(color: Color(0xFF78350F), borderRadius: BorderRadius.circular(20)),
            child: Text('${reward.pointsRequired} pts', style: TextStyle(color: Color(0xFFFCD34D), fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildLedgerCard(LedgerEntry entry) {
    return Container(
      margin: EdgeInsets.only(bottom: 8),
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(entry.points > 0 ? Icons.add_circle : Icons.remove_circle, color: entry.points > 0 ? Colors.green : Colors.red),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(entry.transactionTypeDisplay, style: TextStyle(color: Colors.white, fontSize: 14)),
                Text(entry.description, style: TextStyle(color: Colors.grey, fontSize: 12), maxLines: 1, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          Text('${entry.points > 0 ? '+' : ''}${entry.points}', style: TextStyle(color: entry.points > 0 ? Colors.green : Colors.red, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}