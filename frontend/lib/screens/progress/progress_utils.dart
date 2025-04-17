// lib/screens/progress/progress_utils.dart
import 'package:flutter/material.dart';

Widget buildProgressScreen({
  required String message,
  required double progressValue,
}) {
  return Scaffold(
    body: Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          LinearProgressIndicator(
            value: progressValue,
            backgroundColor: Colors.grey[300],
            color: Colors.green,
            minHeight: 6,
          ),
          SizedBox(height: 20),
          Text(message),
        ],
      ),
    ),
  );
}
