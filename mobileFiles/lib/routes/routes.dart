import 'package:flutter/material.dart';
import 'package:mobile/screens/LoginScreen.dart';
import 'package:mobile/screens/RegisterScreen.dart';
import 'package:mobile/screens/CardsScreen.dart';
import 'package:mobile/screens/LandingScreen.dart'; // 👈 ADD THIS
import 'package:mobile/screens/ForgotPasswordScreen.dart';

class Routes {
  static const String LOGINSCREEN = '/login';
  static const String REGISTERSCREEN = '/register';
  static const String CARDSSCREEN = '/cards';
  static const String APITESTSCREEN = '/apitest';
  static const String FORGOTPASSWORDSCREEN = '/forgot-password';

  static Map<String, Widget Function(BuildContext)> get getroutes => {
    '/': (context) => const LandingScreen(), // 👈 default screen
    LOGINSCREEN: (context) => const LoginScreen(),
    REGISTERSCREEN: (context) => const RegisterScreen(),
    CARDSSCREEN: (context) => const CardsScreen(),
    FORGOTPASSWORDSCREEN: (context) => const ForgotPasswordScreen(),
  };
}