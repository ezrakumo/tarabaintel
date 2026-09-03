import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

class OfflineQueue {
  static const String _fileName = 'pending_reports.json';

  // Get the local file path
  Future<File> _getLocalFile() async {
    final directory = await getApplicationDocumentsDirectory();
    return File('${directory.path}/$_fileName');
  }

  // Save a report draft locally
  Future<void> saveDraft(Map<String, dynamic> reportData) async {
    final file = await _getLocalFile();
    List<Map<String, dynamic>> drafts = [];

    // Read existing drafts
    if (await file.exists()) {
      String contents = await file.readAsString();
      drafts = List<Map<String, dynamic>>.from(json.decode(contents));
    }

    // Add new draft
    drafts.add(reportData);

    // Save back to file
    await file.writeAsString(json.encode(drafts));
  }

  // Get all pending drafts
  Future<List<Map<String, dynamic>>> getDrafts() async {
    final file = await _getLocalFile();
    if (await file.exists()) {
      String contents = await file.readAsString();
      return List<Map<String, dynamic>>.from(json.decode(contents));
    }
    return [];
  }

  // Clear drafts (after successful sync)
  Future<void> clearDrafts() async {
    final file = await _getLocalFile();
    if (await file.exists()) {
      await file.delete();
    }
  }

  // Remove a specific draft after it syncs successfully
  Future<void> removeDraft(Map<String, dynamic> draft) async {
    List<Map<String, dynamic>> drafts = await getDrafts();
    drafts.remove(draft);
    final file = await _getLocalFile();
    await file.writeAsString(json.encode(drafts));
  }
}