import 'package:flutter/material.dart';
import 'screens/login.dart';
import 'screens/sign_in.dart';
import 'screens/sign_up.dart';
import 'screens/home_screen.dart'; // Import HomeScreen
import 'screens/progress/progress.scrape1.dart';
import 'screens/progress/progress_auth.dart';
import 'screens/progress/progress_done.dart';
import 'screens/progress/progress_scrape2.dart';
import 'screens/schedules_screen.dart';

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
        '/home': (context) => HomeScreen(), // New Route
        '/progress-auth': (context) => ProgressAuthScreen(),
        '/progress-scrape-1': (context) => ProgressScrape1Screen(),
        '/progress-scrape-2': (context) => ProgressScrape2Screen(),
        '/progress-done': (context) => ProgressDoneScreen(),
        '/schedules': (context) => SchedulesScreen(),
      },
    );
  }
}
