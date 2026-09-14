class DashboardResponse {
  final Profile profile;
  final List<Transaction> recentTransactions;
  final List<Redemption> activeRedemptions;
  final List<Reward> affordableRewards;
  final String? nextTier;
  final int? pointsToNextTier;

  DashboardResponse({
    required this.profile,
    required this.recentTransactions,
    required this.activeRedemptions,
    required this.affordableRewards,
    this.nextTier,
    this.pointsToNextTier,
  });

  factory DashboardResponse.fromJson(Map<String, dynamic> json) {
    return DashboardResponse(
      profile: Profile.fromJson(json['profile'] is Map ? json['profile'] : {}),
      
      // ✅ BULLETPROOF: Checks if it's actually a List before casting
      recentTransactions: json['recent_transactions'] is List 
          ? (json['recent_transactions'] as List).map((i) => Transaction.fromJson(i as Map<String, dynamic>)).toList() 
          : [],
          
      activeRedemptions: json['active_redemptions'] is List 
          ? (json['active_redemptions'] as List).map((i) => Redemption.fromJson(i as Map<String, dynamic>)).toList() 
          : [],
          
      affordableRewards: json['affordable_rewards'] is List 
          ? (json['affordable_rewards'] as List).map((i) => Reward.fromJson(i as Map<String, dynamic>)).toList() 
          : [],
          
      nextTier: json['next_tier'] as String?,
      pointsToNextTier: json['points_to_next_tier'] as int?,
    );
  }
}

class Profile {
  final int id;
  final String username;
  final String tier;
  final int totalPoints;
  final int lifetimePoints;
  final String codename;
  final bool isVerified;

  Profile({
    required this.id,
    required this.username,
    required this.tier,
    required this.totalPoints,
    required this.lifetimePoints,
    required this.codename,
    required this.isVerified,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'] ?? 0,
      username: json['username'] ?? 'Unknown',
      tier: json['tier'] ?? 'CITIZEN',
      totalPoints: json['total_points'] ?? 0,
      lifetimePoints: json['lifetime_points'] ?? 0,
      codename: json['codename'] ?? json['username'] ?? 'Unknown',
      isVerified: json['is_verified'] ?? false,
    );
  }
}

class Reward {
  final int id;
  final String title;
  final String description;
  final String category;
  final int pointsRequired;
  final bool isAvailable;

  Reward({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.pointsRequired,
    required this.isAvailable,
  });

  factory Reward.fromJson(Map<String, dynamic> json) {
    return Reward(
      id: json['id'] ?? 0,
      title: json['title'] ?? 'Unknown Reward',
      description: json['description'] ?? '',
      category: json['category'] ?? 'GENERAL',
      pointsRequired: json['points_required'] ?? 0,
      isAvailable: json['is_available'] ?? true,
    );
  }
}

class Transaction {
  final int id;
  final int points;
  final String description;
  final DateTime createdAt;

  Transaction({
    required this.id,
    required this.points,
    required this.description,
    required this.createdAt,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] ?? 0,
      points: json['points'] ?? 0,
      description: json['description'] ?? 'Transaction',
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class Redemption {
  final int id;
  final int pointsDeducted;
  final DateTime createdAt;

  Redemption({
    required this.id,
    required this.pointsDeducted,
    required this.createdAt,
  });

  factory Redemption.fromJson(Map<String, dynamic> json) {
    return Redemption(
      id: json['id'] ?? 0,
      pointsDeducted: json['points_deducted'] ?? 0,
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}