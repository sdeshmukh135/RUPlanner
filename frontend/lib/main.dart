import 'package:flutter/material.dart';
import 'screens/login.dart';
import 'screens/sign_in.dart';
import 'screens/sign_up.dart';
import 'screens/home_screen.dart'; // Import HomeScreen

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'DynaSched',
      theme: ThemeData(
        primarySwatch: Colors.green,
        fontFamily: 'Poppins',
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => LoginScreen(),
        '/sign-in': (context) => SignInScreen(),
        '/sign-up': (context) => SignUpScreen(),
        '/home': (context) => HomeScreen(),  // New Route
      },
    );
  }
}

