import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class ConnectivityService {
  final Connectivity _connectivity = Connectivity();
  StreamController<bool> _connectionController = StreamController<bool>.broadcast();

  Stream<bool> get connectionStream => _connectionController.stream;

  ConnectivityService() {
    _connectivity.onConnectivityChanged.listen((result) {
      // In v5.0.2, 'result' is a single ConnectivityResult, not a List
      bool isConnected = result == ConnectivityResult.wifi || 
                         result == ConnectivityResult.mobile ||
                         result == ConnectivityResult.ethernet;
                         
      _connectionController.add(isConnected);
    });
  }

  // Check current connection status
  Future<bool> checkConnection() async {
    var result = await _connectivity.checkConnectivity();
    // In v5.0.2, checkConnectivity returns a single ConnectivityResult
    return result == ConnectivityResult.wifi || 
           result == ConnectivityResult.mobile ||
           result == ConnectivityResult.ethernet;
  }

  void dispose() {
    _connectionController.close();
  }
}