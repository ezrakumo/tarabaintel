class DashboardResponse {
  final String status;
  final String userTier;
  final int totalPoints;
  final int lifetimePoints;
  final List<Reward> affordableRewards;
  final List<Transaction> recentTransactions;
  final String? nextTier;
  final int pointsToNextTier;

  DashboardResponse({
    required this.status,
    required this.userTier,
    required this.totalPoints,
    required this.lifetimePoints,
    required this.affordableRewards,
    required this.recentTransactions,
    this.nextTier,
    required this.pointsToNextTier,
  });

  // ✅ PARSE CAMELCASE KEYS FROM API
  factory DashboardResponse.fromJson(Map<String, dynamic> json) {
    print("🔍 Parsing dashboard JSON: $json"); // Debug log
    
    return DashboardResponse(
      status: json['status'] ?? 'success',
      userTier: json['userTier'] ?? 'CITIZEN',
      totalPoints: json['totalPoints'] ?? 0, // ✅ CAMELCASE!
      lifetimePoints: json['lifetimePoints'] ?? 0,
      affordableRewards: (json['affordableRewards'] as List<dynamic>?)
          ?.map((r) => Reward.fromJson(r))
          .toList() ?? [],
      recentTransactions: (json['recentTransactions'] as List<dynamic>?)
          ?.map((t) => Transaction.fromJson(t))
          .toList() ?? [],
      nextTier: json['nextTier'],
      pointsToNextTier: json['pointsToNextTier'] ?? 0,
    );
  }
}

class Reward {
  final int id;
  final String title;
  final String? description;
  final int pointsRequired;

  Reward({
    required this.id,
    required this.title,
    this.description,
    required this.pointsRequired,
  });

  factory Reward.fromJson(Map<String, dynamic> json) {
    return Reward(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      pointsRequired: json['pointsRequired'] ?? 0, // ✅ CAMELCASE!
    );
  }
}

class Transaction {
  final String type;
  final int points;
  final String description;
  final String? date;

  Transaction({
    required this.type,
    required this.points,
    required this.description,
    this.date,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      type: json['type'] ?? '',
      points: json['points'] ?? 0,
      description: json['description'] ?? '',
      date: json['date'],
    );
  }
}