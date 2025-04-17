import 'package:flutter/material.dart';
import 'dart:async';

class ProgressDoneScreen extends StatefulWidget {
  @override
  _ProgressDoneScreenState createState() => _ProgressDoneScreenState();
}

class _ProgressDoneScreenState extends State<ProgressDoneScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(seconds: 3), () {
      Navigator.pushReplacementNamed(context, '/home');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircleAvatar(
              radius: 40,
              backgroundColor: Colors.black,
              child: Icon(Icons.check, color: Colors.green, size: 50),
            ),
            SizedBox(height: 20),
            Text("Done!", style: TextStyle(fontSize: 20)),
          ],
        ),
      ),
    );
  }
}
