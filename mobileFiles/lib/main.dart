import 'package:flutter/material.dart';
import 'package:mobile/routes/routes.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Professor Selection Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(),

      // 👇 THIS IS THE IMPORTANT LINE
      initialRoute: '/',

      routes: Routes.getroutes,
    );
  }
}