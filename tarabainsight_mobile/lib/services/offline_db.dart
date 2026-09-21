import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class OfflineDb {
  static final OfflineDb instance = OfflineDb._init();
  static Database? _database;

  OfflineDb._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('offline_reports.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);
    return await openDatabase(path, version: 1, onCreate: _createDB);
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE offline_reports (
        id TEXT PRIMARY KEY,
        category TEXT,
        description TEXT,
        lga TEXT,
        lat REAL,
        lon REAL,
        image_base64 TEXT,
        created_at TEXT
      )
    ''');
  }

  Future<void> insertReport(Map<String, dynamic> report) async {
    final db = await instance.database;
    await db.insert('offline_reports', report, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> getUnsyncedReports() async {
    final db = await instance.database;
    return await db.query('offline_reports');
  }

  Future<void> deleteReport(String id) async {
    final db = await instance.database;
    await db.delete('offline_reports', where: 'id = ?', whereArgs: [id]);
  }
}