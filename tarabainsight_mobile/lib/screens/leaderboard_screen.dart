import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({Key? key}) : super(key: key);

  @override
  _LeaderboardScreenState createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _data;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchLeaderboard();
  }

  Future<void> _fetchLeaderboard() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('jwt_token');

      final response = await http.get(
        Uri.parse('https://tarabaintel-ai.onrender.com/api/analytics/leaderboard/'),
        headers: {'Authorization': 'Bearer $token'},
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        setState(() {
          _data = jsonDecode(response.body);
          _isLoading = false;
        });
      } else {
        setState(() { _error = 'Failed to load leaderboard'; _isLoading = false; });
      }
    } catch (e) {
      setState(() { _error = 'Network error'; _isLoading = false; });
    }
  }

  Color _getTierColor(String tier) {
    switch (tier.toUpperCase()) {
      case 'AGENT': return const Color(0xFFEAB308); // Gold
      case 'INFORMANT': return const Color(0xFF94A3B8); // Silver
      case 'VOLUNTEER': return const Color(0xFFB45309); // Bronze
      default: return Colors.grey;
    }
  }

  IconData _getRankIcon(int rank) {
    if (rank == 1) return Icons.emoji_events; // 🥇
    if (rank == 2) return Icons.emoji_events_outlined; // 🥈
    if (rank == 3) return Icons.emoji_events_outlined; // 🥉
    return Icons.person_outline;
  }

  Color _getRankColor(int rank) {
    if (rank == 1) return const Color(0xFFEAB308); // Gold
    if (rank == 2) return const Color(0xFF94A3B8); // Silver
    if (rank == 3) return const Color(0xFFB45309); // Bronze
    return Colors.white54;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E17),
      appBar: AppBar(
        title: const Text('Elite Operatives', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1F2937),
        elevation: 0,
        actions: [
          IconButton(icon: const Icon(Icons.refresh, color: Colors.white), onPressed: _fetchLeaderboard),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFEAB308)))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
              : _data == null
                  ? const Center(child: Text('No data available', style: TextStyle(color: Colors.white)))
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // ✅ CURRENT USER CARD
                          _buildCurrentUserCard(),
                          const SizedBox(height: 24),
                          
                          const Text('TOP AGENTS', style: TextStyle(color: Colors.white54, fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                          const SizedBox(height: 12),
                          
                          // ✅ LEADERBOARD LIST
                          ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: (_data!['top_agents'] as List).length,
                            itemBuilder: (context, index) {
                              final agent = _data!['top_agents'][index];
                              final rank = agent['rank'] as int;
                              final isTopThree = rank <= 3;
                              
                              return Container(
                                margin: const EdgeInsets.only(bottom: 12),
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: isTopThree ? const Color(0xFF1F2937) : const Color(0xFF111827),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: isTopThree ? _getRankColor(rank).withOpacity(0.3) : const Color(0xFF374151),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    // Rank / Icon
                                    Container(
                                      width: 40,
                                      height: 40,
                                      decoration: BoxDecoration(
                                        color: _getRankColor(rank).withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Center(
                                        child: Text(
                                          '#$rank',
                                          style: TextStyle(
                                            color: _getRankColor(rank),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                          ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 16),
                                    
                                    // Name & Tier
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            agent['name'],
                                            style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                                          ),
                                          const SizedBox(height: 4),
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: _getTierColor(agent['tier']).withOpacity(0.2),
                                              borderRadius: BorderRadius.circular(4),
                                            ),
                                            child: Text(
                                              agent['tier'].toString().toUpperCase(),
                                              style: TextStyle(color: _getTierColor(agent['tier']), fontSize: 12, fontWeight: FontWeight.bold),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    
                                    // Points
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.end,
                                      children: [
                                        Text(
                                          '${agent['points']}',
                                          style: const TextStyle(color: Color(0xFFEAB308), fontSize: 18, fontWeight: FontWeight.bold),
                                        ),
                                        const Text('PTS', style: TextStyle(color: Colors.white54, fontSize: 10)),
                                      ],
                                    ),
                                  ],
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildCurrentUserCard() {
    final user = _data!['current_user'];
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFFEAB308), Color(0xFFCA8A04)]),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: const Color(0xFFEAB308).withOpacity(0.2), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: Colors.black.withOpacity(0.2), borderRadius: BorderRadius.circular(12)),
            child: const Icon(Icons.person, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('YOUR RANK', style: TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.bold)),
                Text('#${user['rank']}', style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('${user['points']} Total Points • ${user['tier']}', style: const TextStyle(color: Colors.white, fontSize: 14)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}