import 'package:flutter/material.dart';
import '../widgets/rounded_button.dart';
import 'package:flutter/gestures.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SignInScreen extends StatefulWidget{
  @override
  _SignInScreenState createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String message = '';

  Future<void> login(BuildContext context) async {
    final response = await http.post(
      Uri.parse('http://127.0.0.1:5000/login'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        'username': _usernameController.text,
        'password': _passwordController.text,
      }),
    );

    if (response.statusCode == 200) {
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      final responsebody = jsonDecode(response.body);
      print(responsebody['message']);
      setState(() {
        message = jsonDecode(response.body)['message'];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: Column(
          children: [
            Container(
              height : 300,
              padding: EdgeInsets.symmetric(horizontal: 20, vertical: 40),
              color: Color(0xFF2E2E2E), // Dark grey background
              child: Center(
                child: Image.asset(
                    '/Users/sanikadeshmukh/Desktop/VSCodeProjects/RUPlanner/frontend/lib/assets/images/ds.png',
                    height: 80,
                  ),
              ),
            ),
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: 40.0, vertical: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Sign in',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
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
                    text: 'Sign in',
                    press: () => login(context),
                    //press: () {
                      // Implement your login logic
                      //Navigator.pushNamed(context, '/home'); // Redirect to Home Screen
                    //},
                  ),
                  SizedBox(height: 10),
                  Center(
                    child: TextButton(
                      onPressed: () {},
                      child: Text(
                        'Forgot password?',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
                  ),
                  SizedBox(height: 20),
                  OutlinedButton.icon(
                    onPressed: () {},
                    icon: Image.asset('/Users/sanikadeshmukh/Desktop/VSCodeProjects/RUPlanner/frontend/lib/assets/images/google.png',
                        height: 20),
                    label: Text('Continue with Google'),
                    style: OutlinedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                  ),
                  SizedBox(height: 20),
                  Center(
                    child: Text.rich(
                    TextSpan(
                      text: "Don’t have an account? ",
                      style: TextStyle(color: Colors.grey),
                      children: [
                      TextSpan(
                        text: "Sign Up",
                        style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
                        recognizer: TapGestureRecognizer()..onTap = () {
                        Navigator.pushNamed(context, '/sign-up');
                        },
        ),
      ],
    ),
  ),
)

                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
