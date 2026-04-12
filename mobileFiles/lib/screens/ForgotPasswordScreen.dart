import 'dart:convert';
import 'package:flutter/material.dart';
import '../utils/getAPI.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  String message = '';
  String email = '';

  void setMessage(String text) {
    setState(() {
      message = text;
    });
  }

  Future<void> doForgotPassword() async {
    if (email.trim().isEmpty) {
      setMessage("Please enter your email first");
      return;
    }

    setMessage('');

    final payload = json.encode({
      "email": email.trim(),
    });

    try {
      const url = 'http://10.0.2.2:5001/api/auth/forgot-password';
      final ret = await CardsData.getJson(url, payload);
      final jsonObject = json.decode(ret);

      final String responseMessage =
          jsonObject["msg"] ?? jsonObject["message"] ?? "Something went wrong";

      setMessage(responseMessage);
    } catch (e) {
      setMessage("Error: $e");
    }
  }

  Widget _buildInput(
      String label,
      Function(String) onChanged, {
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
                      '/login',
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
                          "Reset Password",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          "Enter your email and we'll send you a link to get back into your account.",
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: Color(0xFF9E98AE),
                            fontSize: 13,
                            height: 1.5,
                          ),
                        ),
                        const SizedBox(height: 28),
                        _buildInput(
                          "Email",
                              (text) => email = text,
                          hintText: "name@example.com",
                        ),
                        const SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: doForgotPassword,
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
                              "Send Reset Link",
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 18),
                        TextButton(
                          onPressed: () {
                            Navigator.pushNamedAndRemoveUntil(
                              context,
                              '/login',
                                  (route) => false,
                            );
                          },
                          child: const Text(
                            "Back to login",
                            style: TextStyle(
                              color: Color(0xFF9E98AE),
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        if (message.isNotEmpty)
                          Text(
                            message,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: message.toLowerCase().contains("sent")
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