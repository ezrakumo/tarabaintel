class UserProfile {
  final int id;
  final String username;
  final String tier;
  final int totalPoints;
  final int lifetimePoints;

  UserProfile({
    required this.id,
    required this.username,
    required this.tier,
    required this.totalPoints,
    required this.lifetimePoints,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      username: json['username'],
      tier: json['tier'],
      totalPoints: json['total_points'],
      lifetimePoints: json['lifetime_points'],
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
      id: json['id'],
      title: json['title'],
      description: json['description'],
      category: json['category'],
      pointsRequired: json['points_required'],
      isAvailable: json['is_available'],
    );
  }
}

class LedgerEntry {
  final int id;
  final String transactionTypeDisplay;
  final int points;
  final String description;
  final String createdAt;

  LedgerEntry({
    required this.id,
    required this.transactionTypeDisplay,
    required this.points,
    required this.description,
    required this.createdAt,
  });

  factory LedgerEntry.fromJson(Map<String, dynamic> json) {
    return LedgerEntry(
      id: json['id'],
      transactionTypeDisplay: json['transaction_type_display'],
      points: json['points'],
      description: json['description'],
      createdAt: json['created_at'],
    );
  }
}