import 'package:flutter/material.dart';
import 'dart:async';
import 'progress_utils.dart';

class ProgressScrape2Screen extends StatefulWidget {
  @override
  _ProgressScrape2ScreenState createState() => _ProgressScrape2ScreenState();
}

class _ProgressScrape2ScreenState extends State<ProgressScrape2Screen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(seconds: 3), () {
      Navigator.pushReplacementNamed(context, '/progress-done');
    });
  }

  @override
  Widget build(BuildContext context) {
    return buildProgressScreen(
      message: "Scraping WebReg Schedule...",
      progressValue: 0.9,
    );
  }
}
