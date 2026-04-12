import 'package:flutter/material.dart';
import 'package:mobile/routes/routes.dart';

class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> {
  final ScrollController _scrollController = ScrollController();
  final GlobalKey _howItWorksKey = GlobalKey();

  void _scrollToHowItWorks() {
    final context = _howItWorksKey.currentContext;
    if (context != null) {
      Scrollable.ensureVisible(
        context,
        duration: const Duration(milliseconds: 600),
        curve: Curves.easeInOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF03010B),
      body: Container(
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(-0.7, -0.3), // 👈 move glow higher
            radius: 1.5,                  // 👈 stretch outward
            colors: [
              Color(0xFF24104A),
              Color(0xFF090018),
              Color(0xFF03010B),
            ],
            stops: [0.0, 0.55, 1.0],      // 👈 smoother falloff
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            controller: _scrollController,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildTopNav(context),
                  const SizedBox(height: 56),
                  _buildHeroSection(context),
                  const SizedBox(height: 100),
                  _buildDataSection(),
                  const SizedBox(height: 60),
                  _buildHowItWorksSection(),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTopNav(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Text(
          'KnightRate',
          style: TextStyle(
            color: Colors.white,
            fontSize: 26,
            fontWeight: FontWeight.w800,
          ),
        ),
        Row(
          children: [
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, Routes.LOGINSCREEN);
              },
              child: const Text(
                'Log in',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(width: 10),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, Routes.REGISTERSCREEN);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
                elevation: 0,
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              child: const Text(
                'Get started',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHeroSection(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 700),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF1B0B39),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(
                color: const Color(0xFF5B2AA8),
                width: 1,
              ),
            ),
            child: const Text(
              '✦ UCF PROFESSOR RATING PLATFORM',
              style: TextStyle(
                color: Color(0xFFB56CFF),
                fontSize: 14,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.2,
              ),
            ),
          ),
          const SizedBox(height: 28),
          RichText(
            text: const TextSpan(
              children: [
                TextSpan(
                  text: 'Find the right\n',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 52,
                    fontWeight: FontWeight.w900,
                    height: 1.0,
                  ),
                ),
                TextSpan(
                  text: 'professors & courses',
                  style: TextStyle(
                    color: Color(0xFFB56CFF),
                    fontSize: 52,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                TextSpan(
                  text: '\nat UCF.',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 52,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          const SizedBox(
            width: 560,
            child: Text(
              'Our composite scoring algorithm combines 10+ metrics from RateMyProfessor, SPI Surveys, and more — distilled into one clear number.',
              style: TextStyle(
                color: Color(0xFFB9B3C9),
                fontSize: 22,
                height: 1.6,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
          const SizedBox(height: 36),
          Wrap(
            spacing: 16,
            runSpacing: 16,
            children: [
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x664B0D8B),
                      blurRadius: 24,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, Routes.REGISTERSCREEN);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF9B4DFF),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 28,
                      vertical: 20,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Text(
                    'Get started free',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              OutlinedButton(
                onPressed: _scrollToHowItWorks,
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFFB9B3C9),
                  side: const BorderSide(
                    color: Color(0xFF2A2440),
                    width: 1.2,
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 28,
                    vertical: 20,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: const Text(
                  'How it works',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDataSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 8),
      child: Column(
        children: [
          const Text(
            'Built on real data',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 44,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 20),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 760),
            child: const Text(
              'We aggregate data from multiple sources to calculate a unique, trustworthy professor rating.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Color(0xFFACA7BA),
                fontSize: 22,
                height: 1.6,
              ),
            ),
          ),
          const SizedBox(height: 36),
          Wrap(
            alignment: WrapAlignment.center,
            spacing: 16,
            runSpacing: 16,
            children: const [
              _SourcePill(label: '⭐  RateMyProfessor'),
              _SourcePill(label: '📋  SPI Surveys'),
              _SourcePill(label: '🎓  UCF Grade Data'),
              _SourcePill(label: '💼  LinkedIn'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHowItWorksSection() {
    return Container(
      key: _howItWorksKey,
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 30),
      child: Column(
        children: [
          const Text(
            'How It Works',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 38,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            'Understanding how KnightRate scores and classifies professors.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Color(0xFFB9B3C9),
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 30),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(22),
            decoration: BoxDecoration(
              color: const Color(0xFF0B0A14),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                _ScoreRow(
                  title: 'Retake Score',
                  description:
                  'How likely students are to take this professor again, based on RMP and survey data.',
                ),
                SizedBox(height: 24),
                _ScoreRow(
                  title: 'Quality Score',
                  description:
                  'Overall teaching quality derived from RateMyProfessor ratings and SPI survey responses.',
                ),
                SizedBox(height: 24),
                _ScoreRow(
                  title: 'Difficulty Score',
                  description:
                  'How demanding the professor\'s coursework is relative to the UCF average.',
                ),
              ],
            ),
          ),
          const SizedBox(height: 30),
          Wrap(
            spacing: 16,
            runSpacing: 16,
            children: [
              _TypeCard(
                title: 'The Unicorn',
                description:
                'The rarest professor — high scores across the board, easy grader, and beloved by students.',
                imagePath: 'assets/images/unicorn.png',
              ),
              _TypeCard(
                title: 'The Mastermind',
                description:
                'Highly knowledgeable and engaging, but expects a lot from students.',
                imagePath: 'assets/images/brain.png',
              ),
              _TypeCard(
                title: 'The Saboteur',
                description:
                'Poor teaching quality paired with harsh grading. Proceed with caution.',
                imagePath: 'assets/images/bomb.png',
              ),
              _TypeCard(
                title: 'The NPC',
                description:
                'Average in every metric — not particularly good or bad. You get what you put in.',
                imagePath: 'assets/images/bot.png',
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SourcePill extends StatelessWidget {
  final String label;

  const _SourcePill({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
      decoration: BoxDecoration(
        color: const Color(0xFF0A0A0F),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFFCBC4D7),
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
class _ScoreRow extends StatelessWidget {
  final String title;
  final String description;

  const _ScoreRow({
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 130,
          child: Text(
            title,
            style: const TextStyle(
              color: Color(0xFFB56CFF),
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(width: 18),
        Expanded(
          child: Text(
            description,
            style: const TextStyle(
              color: Color(0xFFCBC4D7),
              fontSize: 16,
              height: 1.6,
            ),
          ),
        ),
      ],
    );
  }
}

class _TypeCard extends StatelessWidget {
  final String title;
  final String description;
  final String imagePath;

  const _TypeCard({
    required this.title,
    required this.description,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 330,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0B0A14),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 54,
            height: 54,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: const Color(0xFF171624),
              borderRadius: BorderRadius.circular(14),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Image.asset(
                imagePath,
                width: 40,
                height: 40,
                fit: BoxFit.contain,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  style: const TextStyle(
                    color: Color(0xFFCBC4D7),
                    fontSize: 16,
                    height: 1.6,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}