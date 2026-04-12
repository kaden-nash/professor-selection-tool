import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ApiTestScreen extends StatefulWidget {
  const ApiTestScreen({super.key});

  @override
  State<ApiTestScreen> createState() => _ApiTestScreenState();
}

class _ApiTestScreenState extends State<ApiTestScreen> {
  final String baseUrl = "http://10.0.2.2:5001";
  String output = "Press a button to test an API.";
  bool isLoading = false;

  Future<void> _runRequest(Future<http.Response> Function() request) async {
    setState(() {
      isLoading = true;
      output = "Loading...";
    });

    try {
      final response = await request();

      final prettyJson = _tryPrettyPrint(response.body);

      setState(() {
        output =
        "STATUS: ${response.statusCode}\n\n"
            "BODY:\n$prettyJson";
      });
    } catch (e) {
      setState(() {
        output = "ERROR:\n$e";
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  String _tryPrettyPrint(String body) {
    try {
      final decoded = jsonDecode(body);
      const encoder = JsonEncoder.withIndent('  ');
      return encoder.convert(decoded);
    } catch (_) {
      return body;
    }
  }

  Future<void> testHealthRoute() async {
    await _runRequest(() {
      return http.get(Uri.parse("$baseUrl/"));
    });
  }

  Future<void> testRegister() async {
    await _runRequest(() {
      return http.post(
        Uri.parse("$baseUrl/api/auth/register"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "name": "Greg Test",
          "email": "gregtest123@example.com",
          "password": "123456"
        }),
      );
    });
  }

  Future<void> testLogin() async {
    await _runRequest(() {
      return http.post(
        Uri.parse("$baseUrl/api/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": "gregtest123@example.com",
          "password": "123456"
        }),
      );
    });
  }

  Future<void> testGetCourses() async {
    await _runRequest(() {
      return http.get(Uri.parse("$baseUrl/api/courses"));
    });
  }

  Future<void> testGetProfessors() async {
    await _runRequest(() {
      return http.get(Uri.parse("$baseUrl/api/professors"));
    });
  }

  Future<void> testGetUsers() async {
    await _runRequest(() {
      return http.get(Uri.parse("$baseUrl/api/users"));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("API Test Screen"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                ElevatedButton(
                  onPressed: isLoading ? null : testHealthRoute,
                  child: const Text("Test /"),
                ),
                ElevatedButton(
                  onPressed: isLoading ? null : testRegister,
                  child: const Text("Register"),
                ),
                ElevatedButton(
                  onPressed: isLoading ? null : testLogin,
                  child: const Text("Login"),
                ),
                ElevatedButton(
                  onPressed: isLoading ? null : testGetCourses,
                  child: const Text("Courses"),
                ),
                ElevatedButton(
                  onPressed: isLoading ? null : testGetProfessors,
                  child: const Text("Professors"),
                ),
                ElevatedButton(
                  onPressed: isLoading ? null : testGetUsers,
                  child: const Text("Users"),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SingleChildScrollView(
                  child: Text(
                    output,
                    style: const TextStyle(fontFamily: 'monospace'),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}