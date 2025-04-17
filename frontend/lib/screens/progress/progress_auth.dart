import 'package:flutter/material.dart';
import 'dart:async';
import 'progress_utils.dart';

class ProgressAuthScreen extends StatefulWidget {
  @override
  _ProgressAuthScreenState createState() => _ProgressAuthScreenState();
}

class _ProgressAuthScreenState extends State<ProgressAuthScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(seconds: 3), () {
      Navigator.pushReplacementNamed(context, '/progress-scrape-1');
    });
  }

  @override
  Widget build(BuildContext context) {
    return buildProgressScreen(
      message: "Authenticating Rutgers student...",
      progressValue: 0.3,
    );
  }
}
