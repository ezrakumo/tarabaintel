class DashboardResponse {
  final Profile profile;
  final List<Transaction> recentTransactions;
  final List<Redemption> activeRedemptions;
  final List<Reward> affordableRewards;
  final String nextTier;
  final int pointsToNextTier;

  DashboardResponse({
    required this.profile,
    required this.recentTransactions,
    required this.activeRedemptions,
    required this.affordableRewards,
    required this.nextTier,
    required this.pointsToNextTier,
  });

  factory DashboardResponse.fromJson(Map<String, dynamic> json) {
    return DashboardResponse(
      profile: Profile.fromJson(json['profile']),
      recentTransactions: (json['recent_transactions'] as List).map((i) => Transaction.fromJson(i)).toList(),
      activeRedemptions: (json['active_redemptions'] as List).map((i) => Redemption.fromJson(i)).toList(),
      affordableRewards: (json['affordable_rewards'] as List).map((i) => Reward.fromJson(i)).toList(),
      nextTier: json['next_tier'],
      pointsToNextTier: json['points_to_next_tier'],
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

  Profile({required this.id, required this.username, required this.tier, required this.totalPoints, required this.lifetimePoints, required this.codename, required this.isVerified});

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'], username: json['username'], tier: json['tier'],
      totalPoints: json['total_points'], lifetimePoints: json['lifetime_points'],
      codename: json['codename'] ?? json['username'], isVerified: json['is_verified'],
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

  Reward({required this.id, required this.title, required this.description, required this.category, required this.pointsRequired, required this.isAvailable});

  factory Reward.fromJson(Map<String, dynamic> json) {
    return Reward(
      id: json['id'], title: json['title'], description: json['description'],
      category: json['category'], pointsRequired: json['points_required'], isAvailable: json['is_available'],
    );
  }
}

class Transaction {
  final int id;
  final int points;
  final String description;
  final DateTime createdAt;

  Transaction({required this.id, required this.points, required this.description, required this.createdAt});

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(id: json['id'], points: json['points'], description: json['description'], createdAt: DateTime.parse(json['created_at']));
  }
}

class Redemption {
  final int id;
  final int pointsDeducted;
  final DateTime createdAt;

  Redemption({required this.id, required this.pointsDeducted, required this.createdAt});

  factory Redemption.fromJson(Map<String, dynamic> json) {
    return Redemption(id: json['id'], pointsDeducted: json['points_deducted'], createdAt: DateTime.parse(json['created_at']));
  }
}
