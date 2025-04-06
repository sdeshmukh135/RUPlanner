import 'package:flutter/material.dart';
import '../widgets/rounded_button.dart';
import 'package:flutter/gestures.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SignUpScreen extends StatefulWidget{
  @override
  _SignUpScreenState createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String message = '';

  Future<void> signup(BuildContext context) async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:5000/signup'),  // Replace with your Flask server URL
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        'username': _usernameController.text,
        'password': _passwordController.text,
      }),
    );

    if (response.statusCode == 201) {
      Navigator.pushNamed(context, '/home');  // ✅ Navigate to Home on successful signup
    }
    else if (response.statusCode == 400){
      final responsebody = jsonDecode(response.body);
      _showSnackbar(context, responsebody['message'], isSuccess: false); // not a success
      setState(() {
        message = responsebody['message'];  // Display message on the screen as well
      });
    }
    else {
      setState(() {
        message = jsonDecode(response.body)['message'];
      });
    }
  }

  // to get a pop-up to show whether or not the user needs to include another username or password
  void _showSnackbar(BuildContext context, String message, {required bool isSuccess}) {
    final snackBar = SnackBar(
      content: Text(
        message,
        style: TextStyle(color: Colors.white),
      ),
      backgroundColor: isSuccess ? Colors.green : Colors.red, // change to work with the theme 
      duration: Duration(seconds: 3),  // Automatically disappears after 3 seconds
    );

    ScaffoldMessenger.of(context).showSnackBar(snackBar);  // ✅ Display the Snackbar
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: Column(
          children: [
            Container(
              height: 300, 
              padding: EdgeInsets.symmetric(horizontal: 20, vertical: 40),
              color: Color(0xFF2E2E2E),
              child: Center(
                child: Image.asset(
                    '/Users/sanikadeshmukh/Desktop/VSCodeProjects/RUPlanner/frontend/lib/assets/images/ds.png',
                    height: 80,
                  ),
              ),
            ),
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(40),
                  topRight: Radius.circular(40),
                ),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 40.0, vertical: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Sign Up',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 20),
                  TextField(
                    decoration: InputDecoration(
                      hintText: 'Email',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      filled: true,
                      fillColor: Colors.grey[200],
                    ),
                  ),
                  SizedBox(height: 20),
                  TextField(
                    controller: _usernameController,
                    decoration: InputDecoration(
                      hintText: 'Username',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      filled: true,
                      fillColor: Colors.grey[200],
                    ),
                  ),
                  SizedBox(height: 20),
                  TextField(
                    controller: _passwordController,
                    decoration: InputDecoration(
                      hintText: 'Password',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      filled: true,
                      fillColor: Colors.grey[200],
                    ),
                    obscureText: true,
                  ),
                  SizedBox(height: 20),
                  RoundedButton(
                    text: 'Create Account',
                    press: () => signup(context),
                    //press: () {
                      // Handle Sign Up logic
                   // },
                  ),
                  SizedBox(height: 20),
                  Center(
                    child: Text.rich(
                      TextSpan(
                        text: "Already have an account? ",
                        style: TextStyle(color: Colors.grey),
                        children: [
                          TextSpan(
                            text: "Sign in",
                            style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
                            recognizer: TapGestureRecognizer()..onTap = () {
                              Navigator.pushNamed(context, '/sign-in');
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
