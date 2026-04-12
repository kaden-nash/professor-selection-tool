import 'dart:convert';
import 'package:flutter/material.dart';
import '../utils/getAPI.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  String message = '';
  String name = '';
  String email = '';
  String password = '';

  void setMessage(String text) {
    setState(() {
      message = text;
    });
  }

  Future<void> doRegister() async {
    setMessage('');

    final payload = json.encode({
      "name": name.trim(),
      "email": email.trim(),
      "password": password.trim(),
    });

    try {
      const url = 'http://10.0.2.2:5001/api/auth/register';
      final ret = await CardsData.getJson(url, payload);
      final jsonObject = json.decode(ret);

      final String responseMessage =
          jsonObject["msg"] ?? jsonObject["message"] ?? "Something went wrong";

      // Always show backend message
      setMessage(responseMessage);

      // If it's a success → wait → go to login
      if (responseMessage.toLowerCase().contains("successful")) {
        await Future.delayed(const Duration(seconds: 3));
        if (!mounted) return;
        Navigator.pushNamed(context, '/login');
      }
    } catch (e) {
      setMessage("Error: $e");
    }
  }

  Widget _buildInput(
      String label,
      Function(String) onChanged, {
        bool obscure = false,
        String? hintText,
      }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFFB9B3C9),
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          obscureText: obscure,
          onChanged: onChanged,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            hintText: hintText,
            hintStyle: const TextStyle(color: Color(0xFF6F6A7E)),
            filled: true,
            fillColor: const Color(0xFF171624),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 18,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF2A2440)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF2A2440)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF9B4DFF)),
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF03010B),
      body: Container(
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(0, -1.1),
            radius: 1.6,
            colors: [
              Color(0xFF24104A),
              Color(0xFF090018),
              Color(0xFF03010B),
            ],
            stops: [0.0, 0.45, 1.0],
          ),
        ),
        child: SafeArea(
          child: Stack(
            children: [
              Positioned(
                top: 8,
                left: 8,
                child: IconButton(
                  icon: const Icon(Icons.arrow_back, color: Colors.white),
                  onPressed: () {
                    Navigator.pushNamedAndRemoveUntil(
                      context,
                      '/',
                          (route) => false,
                    );
                  },
                ),
              ),
              Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Container(
                    width: 360,
                    padding: const EdgeInsets.all(28),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0B0A14),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: const Color(0xFF1C1A2E)),
                      boxShadow: const [
                        BoxShadow(
                          color: Color(0x33000000),
                          blurRadius: 30,
                          spreadRadius: 4,
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Text(
                          "Create Account",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text(
                              "Already have an account yet? ",
                              style: TextStyle(
                                color: Color(0xFF9E98AE),
                                fontSize: 13,
                              ),
                            ),
                            GestureDetector(
                              onTap: () {
                                Navigator.pushNamed(context, '/login');
                              },
                              child: const Text(
                                "Log in",
                                style: TextStyle(
                                  color: Color(0xFFB56CFF),
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 28),
                        _buildInput(
                          "Full Name",
                              (text) => name = text,
                          hintText: "John Doe",
                        ),
                        const SizedBox(height: 18),
                        _buildInput(
                          "Email",
                              (text) => email = text,
                          hintText: "john@example.com",
                        ),
                        const SizedBox(height: 18),
                        _buildInput(
                          "Password",
                              (text) => password = text,
                          obscure: true,
                          hintText: "Create a password",
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: doRegister,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF9B4DFF),
                              foregroundColor: Colors.white,
                              elevation: 0,
                              padding: const EdgeInsets.symmetric(vertical: 18),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14),
                              ),
                            ),
                            child: const Text(
                              "Register",
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 14),
                        if (message.isNotEmpty)
                          Text(
                            message,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: message.toLowerCase().contains("successful")
                                  ? Colors.greenAccent
                                  : Colors.redAccent,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}