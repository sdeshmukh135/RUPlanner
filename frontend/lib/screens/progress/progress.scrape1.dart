import 'package:flutter/material.dart';
import 'dart:async';
import 'progress_utils.dart';

class ProgressScrape1Screen extends StatefulWidget {
  @override
  _ProgressScrape1ScreenState createState() => _ProgressScrape1ScreenState();
}

class _ProgressScrape1ScreenState extends State<ProgressScrape1Screen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(seconds: 3), () {
      Navigator.pushReplacementNamed(context, '/progress-scrape-2');
    });
  }

  @override
  Widget build(BuildContext context) {
    return buildProgressScreen(
      message: "Scraping WebReg Schedule...",
      progressValue: 0.6,
    );
  }
}
