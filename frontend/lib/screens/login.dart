import 'package:flutter/material.dart';
import '../widgets/rounded_button.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LoginScreen extends StatelessWidget {


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          Expanded(
            flex: 2,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 80),
              color: Color(0xFF2E2E2E), // Dark grey background
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Image.asset(
                    '/Users/sanikadeshmukh/Desktop/VSCodeProjects/RUPlanner/frontend/lib/assets/images/logoschedule.png',
                    height: 150,
                  ),
                  SizedBox(height: 20),
                  Text(
                    'DynaSched',
                    style: TextStyle(
                      fontSize: 40,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 10),
                  Text(
                    'Your dynamic schedule planner.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            flex: 1,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  RoundedButton(
                    text: 'Sign In',
                    press: () {
                      Navigator.pushNamed(context, '/sign-in'); // Navigation Trigger
                    },
                  ),
                  SizedBox(height: 20),
                  RoundedButton(
                    text: 'Sign Up',
                    press: () {
                      // Navigate to Sign Up Screen
                      Navigator.pushNamed(context, '/sign-up');
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
