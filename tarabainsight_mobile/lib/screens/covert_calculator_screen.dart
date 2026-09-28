import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'login_screen.dart'; // Or your AuthWrapper

class CovertCalculatorScreen extends StatefulWidget {
  const CovertCalculatorScreen({Key? key}) : super(key: key);

  @override
  _CovertCalculatorScreenState createState() => _CovertCalculatorScreenState();
}

class _CovertCalculatorScreenState extends State<CovertCalculatorScreen> {
  String _display = '0';
  String _secretPin = '2026'; // ✅ THE SECRET PIN TO UNLOCK THE APP

  void _onButtonPressed(String btn) async {
    if (btn == 'C') {
      setState(() => _display = '0');
    } else if (btn == '=') {
      // ✅ CHECK FOR SECRET PIN
      if (_display == _secretPin) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('is_covert_mode', false); // Unlock the app
        
        if (mounted) {
          Navigator.pushAndRemoveUntil(
            context,
            MaterialPageRoute(builder: (context) => const LoginScreen()), // Route to real app
            (route) => false,
          );
        }
      } else {
        // ✅ BASIC MATH LOGIC TO LOOK REALISTIC
        try {
          // Simple evaluation for basic math to pass casual inspection
          double result = _evaluateMath(_display);
          setState(() => _display = result.toStringAsFixed(2).replaceAll('.00', ''));
        } catch (e) {
          setState(() => _display = 'Error');
        }
      }
    } else {
      setState(() {
        if (_display == '0' || _display == 'Error') {
          _display = btn;
        } else {
          _display += btn;
        }
      });
    }
  }

  // A simple math evaluator to make the disguise convincing
  double _evaluateMath(String expr) {
    expr = expr.replaceAll('×', '*').replaceAll('÷', '/');
    List<String> parts = expr.split(RegExp(r'(?=[+\-×÷])|(?<=[+\-×÷])'));
    double result = double.parse(parts[0]);
    for (int i = 1; i < parts.length; i += 2) {
      double val = double.parse(parts[i + 1]);
      if (parts[i] == '+') result += val;
      else if (parts[i] == '-') result -= val;
      else if (parts[i] == '*') result *= val;
      else if (parts[i] == '/') result /= val;
    }
    return result;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Column(
          children: [
            // Display
            Expanded(
              flex: 2,
              child: Container(
                alignment: Alignment.bottomRight,
                padding: const EdgeInsets.all(20),
                child: Text(
                  _display,
                  style: const TextStyle(color: Colors.white, fontSize: 60, fontWeight: FontWeight.w300),
                ),
              ),
            ),
            // Buttons
            Expanded(
              flex: 5,
              child: GridView.count(
                crossAxisCount: 4,
                children: [
                  _buildButton('C', Colors.grey.shade800, Colors.white),
                  _buildButton('±', Colors.grey.shade800, Colors.white),
                  _buildButton('%', Colors.grey.shade800, Colors.white),
                  _buildButton('÷', Colors.orange, Colors.white),
                  _buildButton('7', Colors.grey.shade900, Colors.white),
                  _buildButton('8', Colors.grey.shade900, Colors.white),
                  _buildButton('9', Colors.grey.shade900, Colors.white),
                  _buildButton('×', Colors.orange, Colors.white),
                  _buildButton('4', Colors.grey.shade900, Colors.white),
                  _buildButton('5', Colors.grey.shade900, Colors.white),
                  _buildButton('6', Colors.grey.shade900, Colors.white),
                  _buildButton('-', Colors.orange, Colors.white),
                  _buildButton('1', Colors.grey.shade900, Colors.white),
                  _buildButton('2', Colors.grey.shade900, Colors.white),
                  _buildButton('3', Colors.grey.shade900, Colors.white),
                  _buildButton('+', Colors.orange, Colors.white),
                  _buildButton('0', Colors.grey.shade900, Colors.white, isWide: true),
                  _buildButton('.', Colors.grey.shade900, Colors.white),
                  _buildButton('=', Colors.orange, Colors.white),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildButton(String text, Color color, Color textColor, {bool isWide = false}) {
    return GestureDetector(
      onTap: () => _onButtonPressed(text),
      child: Container(
        margin: const EdgeInsets.all(2),
        decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(50)),
        child: Center(
          child: Text(
            text,
            style: TextStyle(color: textColor, fontSize: isWide ? 28 : 32, fontWeight: FontWeight.w500),
          ),
        ),
      ),
    );
  }
}