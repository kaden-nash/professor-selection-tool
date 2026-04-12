import 'dart:convert';
import 'dart:io';
import '../utils/session.dart';

import 'package:flutter/material.dart';

class CardsScreen extends StatefulWidget {
  const CardsScreen({super.key});

  @override
  State<CardsScreen> createState() => _CardsScreenState();
}

class _CardsScreenState extends State<CardsScreen> {
  int selectedTab = 0;
  final List<String> tabs = ['About', 'Search', 'Starred', 'Settings'];

  final TextEditingController _searchController = TextEditingController();

  String searchMode = 'name'; // 'name' or 'course'
  String lastQuery = '';
  bool hasSearched = false;
  bool isLoading = false;
  String searchMessage = '';

  List<Map<String, dynamic>> professorResults = [];
  List<Map<String, dynamic>> starredProfessors = [];
  final Set<String> expandedProfessorIds = {};
  final Set<String> starredProfessorIds = {};

  @override
  void initState() {
    super.initState();
    _loadStarredProfessors();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _runSearch() async {
    final query = _searchController.text.trim();

    if (query.isEmpty) {
      setState(() {
        searchMessage = 'Please enter a search term';
        hasSearched = false;
        professorResults = [];
        expandedProfessorIds.clear();
      });
      return;
    }

    setState(() {
      isLoading = true;
      searchMessage = '';
      hasSearched = true;
      lastQuery = query;
      professorResults = [];
      expandedProfessorIds.clear();
    });

    try {
      final results = searchMode == 'name'
          ? await _searchProfessorsByName(query)
          : await _searchProfessorsByCourse(query);

      setState(() {
        professorResults = results;
        isLoading = false;

        if (results.isEmpty) {
          searchMessage = 'No professors found';
        } else {
          final firstId = _professorId(results.first);
          if (firstId.isNotEmpty) {
            expandedProfessorIds.add(firstId);
          }
        }
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        searchMessage = 'Search failed: $e';
      });
    }
  }

  Future<List<Map<String, dynamic>>> _searchProfessorsByName(String query) async {
    final uri = Uri.parse(
      'http://10.0.2.2:5001/api/professors/search?filter=name&q=${Uri.encodeComponent(query)}',
    );

    final response = await _httpGetJson(uri);

    if (response is List) {
      return response.map((e) => Map<String, dynamic>.from(e)).toList();
    }

    return [];
  }

  Future<List<Map<String, dynamic>>> _searchProfessorsByCourse(String query) async {
    final uri = Uri.parse(
      'http://10.0.2.2:5001/api/professors/search?filter=course&q=${Uri.encodeComponent(query)}',
    );

    final response = await _httpGetJson(uri);

    if (response is List) {
      return response.map((e) => Map<String, dynamic>.from(e)).toList();
    }

    return [];
  }
  Future<void> _loadStarredProfessors() async {
    if (Session.token.isEmpty) return;

    final client = HttpClient();
    try {
      final uri = Uri.parse('http://10.0.2.2:5001/api/users/starred');
      final request = await client.getUrl(uri);
      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json');
      request.headers.set(HttpHeaders.authorizationHeader, 'Bearer ${Session.token}');

      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();

      if (response.statusCode >= 200 && response.statusCode < 300) {
        final decoded = json.decode(body);

        if (decoded is List) {
          final loaded = decoded
              .map((e) => Map<String, dynamic>.from(e))
              .toList();

          setState(() {
            starredProfessors = loaded;
            starredProfessorIds
              ..clear()
              ..addAll(
                loaded
                    .map((prof) => _professorId(prof))
                    .where((id) => id.isNotEmpty),
              );
          });
        }
      }
    } catch (_) {
      // ignore for MVP
    } finally {
      client.close();
    }
  }

  Future<dynamic> _httpGetJson(Uri uri) async {
    final client = HttpClient();
    try {
      final request = await client.getUrl(uri);
      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json');

      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();

      final decoded = json.decode(body);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return decoded;
      }

      if (decoded is Map<String, dynamic>) {
        throw decoded['msg'] ?? decoded['message'] ?? 'Request failed';
      }

      throw 'Request failed';
    } finally {
      client.close();
    }
  }

  String _professorId(Map<String, dynamic> professor) {
    return (professor['_id'] ?? '').toString();
  }

  void _toggleExpanded(String professorId) {
    setState(() {
      if (expandedProfessorIds.contains(professorId)) {
        expandedProfessorIds.remove(professorId);
      } else {
        expandedProfessorIds.clear();
        expandedProfessorIds.add(professorId);
      }
    });
  }

  Future<void> _toggleStar(String professorId, Map<String, dynamic> professor) async {
    if (Session.token.isEmpty) {
      setState(() {
        searchMessage = 'You must be logged in to star professors';
      });
      return;
    }

    final isCurrentlyStarred = starredProfessorIds.contains(professorId);
    final client = HttpClient();

    try {
      final uri = Uri.parse('http://10.0.2.2:5001/api/users/starred/$professorId');
      final request = isCurrentlyStarred
          ? await client.deleteUrl(uri)
          : await client.postUrl(uri);

      request.headers.set(HttpHeaders.contentTypeHeader, 'application/json');
      request.headers.set(HttpHeaders.authorizationHeader, 'Bearer ${Session.token}');

      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();

      if (response.statusCode >= 200 && response.statusCode < 300) {
        setState(() {
          if (isCurrentlyStarred) {
            starredProfessorIds.remove(professorId);
            starredProfessors.removeWhere(
                  (p) => _professorId(p) == professorId,
            );
          } else {
            starredProfessorIds.add(professorId);

            final alreadyInList = starredProfessors.any(
                  (p) => _professorId(p) == professorId,
            );

            if (!alreadyInList) {
              starredProfessors.add(Map<String, dynamic>.from(professor));
            }
          }
        });
      } else {
        final decoded = json.decode(body);
        setState(() {
          searchMessage = decoded["msg"] ?? decoded["message"] ?? 'Star action failed';
        });
      }
    } catch (e) {
      setState(() {
        searchMessage = 'Star action failed: $e';
      });
    } finally {
      client.close();
    }
  }

  String _fullName(Map<String, dynamic> professor) {
    final first = (professor['firstName'] ?? '').toString();
    final last = (professor['lastName'] ?? '').toString();
    return '$first $last'.trim();
  }

  String _initials(Map<String, dynamic> professor) {
    final first = (professor['firstName'] ?? '').toString();
    final last = (professor['lastName'] ?? '').toString();

    final a = first.isNotEmpty ? first[0] : '';
    final b = last.isNotEmpty ? last[0] : '';

    return '$a$b'.toUpperCase();
  }

  double _scoreValue(Map<String, dynamic> professor, String key) {
    final value = professor[key];
    if (value is num) return value.toDouble().clamp(0, 100);
    return 0;
  }

  String _scoreText(Map<String, dynamic> professor, String key) {
    return _scoreValue(professor, key).toStringAsFixed(2).replaceAll(RegExp(r'\.00$'), '');
  }

  String _archetypeImage(String archetype) {
    switch (archetype) {
      case 'The Unicorn':
        return 'assets/images/unicorn.png';
      case 'The Mastermind':
        return 'assets/images/brain.png';
      case 'The Saboteur':
        return 'assets/images/bomb.png';
      case 'The NPC':
      default:
        return 'assets/images/bot.png';
    }
  }

  String _archetypeDescription(String archetype) {
    switch (archetype) {
      case 'The Unicorn':
        return 'GPA savior, top tier teaching, zero stress.';
      case 'The Mastermind':
        return 'Challenging but rewarding. High quality instruction.';
      case 'The Saboteur':
        return 'Proceed with caution. High risk, high stress.';
      case 'The NPC':
      default:
        return 'Gets the job done. Nothing more, nothing less.';
    }
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
          child: Column(
            children: [
              _buildTopNav(),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                  child: _buildCurrentTab(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopNav() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        children: [
          const Text(
            'KnightRate',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 26,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(tabs.length, (index) {
              final isActive = selectedTab == index;

              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: TextButton(
                    onPressed: () {
                      setState(() {
                        selectedTab = index;
                      });

                      if (index == 2) {
                        _loadStarredProfessors();
                      }
                    },
                    style: TextButton.styleFrom(
                      backgroundColor:
                      isActive ? const Color(0xFF171624) : Colors.transparent,
                      foregroundColor:
                      isActive ? Colors.white : const Color(0xFFB9B3C9),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    child: Text(
                      tabs[index],
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentTab() {
    switch (selectedTab) {
      case 0:
        return _buildAboutTab();
      case 1:
        return _buildSearchTab();
      case 2:
        return _buildStarredTab();
      case 3:
        return _buildSettingsTab();
      default:
        return _buildAboutTab();
    }
  }

  Widget _buildPlaceholderTab(String text) {
    return SizedBox(
      height: 500,
      child: Center(
        child: Text(
          text,
          style: const TextStyle(
            color: Color(0xFFB9B3C9),
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }

  Widget _buildSearchTab() {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 700),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 10),
            Text(
              hasSearched ? 'Results for: $lastQuery' : 'Find a professor',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 38,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              hasSearched
                  ? 'Top professor matches'
                  : 'Search by name or course and see top professor matches',
              style: const TextStyle(
                color: Color(0xFFB9B3C9),
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 28),
            _buildSearchModeToggle(),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    onSubmitted: (_) => _runSearch(),
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: searchMode == 'name'
                          ? 'Search professors...'
                          : 'Search courses...',
                      hintStyle: const TextStyle(color: Color(0xFF6F6A7E)),
                      filled: true,
                      fillColor: const Color(0xFF171624),
                      prefixIcon: const Icon(Icons.search, color: Color(0xFF6F6A7E)),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 18,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: isLoading ? null : _runSearch,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF9B4DFF),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: const Color(0xFF4B3B66),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 20,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: Text(isLoading ? '...' : 'Search'),
                ),
              ],
            ),
            const SizedBox(height: 24),
            if (searchMessage.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(
                  searchMessage,
                  style: const TextStyle(
                    color: Colors.redAccent,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            if (isLoading)
              const Padding(
                padding: EdgeInsets.only(top: 24),
                child: Center(
                  child: CircularProgressIndicator(
                    color: Color(0xFF9B4DFF),
                  ),
                ),
              ),
            if (!isLoading)
              ...professorResults.map((professor) {
                final id = _professorId(professor);
                final isExpanded = expandedProfessorIds.contains(id);

                return Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: _ProfessorCard(
                    professor: professor,
                    isExpanded: isExpanded,
                    isStarred: starredProfessorIds.contains(id),
                    onTap: () => _toggleExpanded(id),
                    onStarTap: () => _toggleStar(id, professor),
                    archetypeImage: _archetypeImage(
                      (professor['archetype'] ?? 'The NPC').toString(),
                    ),
                    archetypeDescription: _archetypeDescription(
                      (professor['archetype'] ?? 'The NPC').toString(),
                    ),
                    initials: _initials(professor),
                    fullName: _fullName(professor),
                    retakeScore: _scoreValue(professor, 'retakeScore'),
                    qualityScore: _scoreValue(professor, 'qualityScore'),
                    difficultyScore: _scoreValue(professor, 'difficultyScore'),
                    overallScore: _scoreValue(professor, 'overallScore'),
                    lastTimeTaught: (professor['lastTimeTaught'] ?? 'Unknown').toString(),
                    isPolarizing: (professor['isPolarizing'] ?? false) == true,
                    rmpTags: ((professor['rmpTags'] ?? []) as List)
                        .map((e) => e.toString())
                        .toList(),
                  ),
                );
              }),
            if (!isLoading && hasSearched && professorResults.isEmpty && searchMessage.isEmpty)
              const Padding(
                padding: EdgeInsets.only(top: 24),
                child: Text(
                  'No results found',
                  style: TextStyle(
                    color: Color(0xFFB9B3C9),
                    fontSize: 16,
                  ),
                ),
              ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchModeToggle() {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFF171624),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildTogglePill(
            label: 'Name',
            value: 'name',
          ),
          _buildTogglePill(
            label: 'Course',
            value: 'course',
          ),
        ],
      ),
    );
  }

  Widget _buildStarredTab() {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 700),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 10),
            const Text(
              'Starred Professors',
              style: TextStyle(
                color: Colors.white,
                fontSize: 38,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Your saved professors',
              style: TextStyle(
                color: Color(0xFFB9B3C9),
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 24),
            if (starredProfessors.isEmpty)
              const Text(
                'No starred professors yet',
                style: TextStyle(
                  color: Color(0xFFB9B3C9),
                  fontSize: 16,
                ),
              ),
            ...starredProfessors.map((professor) {
              final id = _professorId(professor);
              final isExpanded = expandedProfessorIds.contains(id);

              return Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: _ProfessorCard(
                  professor: professor,
                  isExpanded: isExpanded,
                  isStarred: true,
                  onTap: () => _toggleExpanded(id),
                  onStarTap: () => _toggleStar(id, professor),
                  archetypeImage: _archetypeImage(
                    (professor['archetype'] ?? 'The NPC').toString(),
                  ),
                  archetypeDescription: _archetypeDescription(
                    (professor['archetype'] ?? 'The NPC').toString(),
                  ),
                  initials: _initials(professor),
                  fullName: _fullName(professor),
                  retakeScore: _scoreValue(professor, 'retakeScore'),
                  qualityScore: _scoreValue(professor, 'qualityScore'),
                  difficultyScore: _scoreValue(professor, 'difficultyScore'),
                  overallScore: _scoreValue(professor, 'overallScore'),
                  lastTimeTaught: (professor['lastTimeTaught'] ?? 'Unknown').toString(),
                  isPolarizing: (professor['isPolarizing'] ?? false) == true,
                  rmpTags: ((professor['rmpTags'] ?? []) as List)
                      .map((e) => e.toString())
                      .toList(),
                ),
              );
            }),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  Widget _buildTogglePill({
    required String label,
    required String value,
  }) {
    final isActive = searchMode == value;

    return GestureDetector(
      onTap: () {
        setState(() {
          searchMode = value;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 12),
        decoration: BoxDecoration(
          color: isActive ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isActive ? Colors.black : const Color(0xFFB9B3C9),
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }

  Widget _buildAboutTab() {
    return Column(
      children: [
        const SizedBox(height: 20),
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
        const SizedBox(height: 32),
        Container(
          constraints: const BoxConstraints(maxWidth: 760),
          width: double.infinity,
          padding: const EdgeInsets.all(22),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0A14),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Column(
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
        const SizedBox(height: 32),
        Wrap(
          alignment: WrapAlignment.center,
          spacing: 16,
          runSpacing: 16,
          children: const [
            _TypeCard(
              title: 'The Unicorn',
              description:
              'The rarest professor — high scores across the board, easy grader, and beloved by students. GPA savior, top tier teaching, zero stress.',
              imagePath: 'assets/images/unicorn.png',
            ),
            _TypeCard(
              title: 'The Mastermind',
              description:
              'Highly knowledgeable and engaging, but expects a lot from students. Challenging but ultimately rewarding.',
              imagePath: 'assets/images/brain.png',
            ),
            _TypeCard(
              title: 'The Saboteur',
              description:
              'Poor teaching quality paired with harsh grading. Students often feel set up to fail. Proceed with caution.',
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
        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildSettingsTab() {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 20),
            const Text(
              'Settings',
              style: TextStyle(
                color: Colors.white,
                fontSize: 38,
                fontWeight: FontWeight.w900,
              ),
            ),
            const SizedBox(height: 28),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 24),
              decoration: BoxDecoration(
                color: const Color(0xFF0B0A14),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'ACCOUNT',
                    style: TextStyle(
                      color: Color(0xFF7F7895),
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 26),
                  _buildSettingRow('Email', '—'),
                  const SizedBox(height: 24),
                  _buildSettingRow('Password', '••••••••'),
                ],
              ),
            ),
            const SizedBox(height: 36),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {
                  Session.token = '';
                  starredProfessorIds.clear();
                  starredProfessors.clear();
                  Navigator.pushNamedAndRemoveUntil(
                    context,
                    '/',
                        (route) => false,
                  );
                },
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFFFF6B81),
                  side: const BorderSide(
                    color: Color(0xFF5A2330),
                    width: 1.2,
                  ),
                  backgroundColor: const Color(0xFF1A0B12),
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: const Text(
                  'Sign out',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingRow(String label, String value) {
    return Row(
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFFCBC4D7),
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            color: Color(0xFF7F7895),
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _ProfessorCard extends StatelessWidget {
  final Map<String, dynamic> professor;
  final bool isExpanded;
  final bool isStarred;
  final VoidCallback onTap;
  final VoidCallback onStarTap;
  final String archetypeImage;
  final String archetypeDescription;
  final String initials;
  final String fullName;
  final double retakeScore;
  final double qualityScore;
  final double difficultyScore;
  final double overallScore;
  final String lastTimeTaught;
  final bool isPolarizing;
  final List<String> rmpTags;

  const _ProfessorCard({
    required this.professor,
    required this.isExpanded,
    required this.isStarred,
    required this.onTap,
    required this.onStarTap,
    required this.archetypeImage,
    required this.archetypeDescription,
    required this.initials,
    required this.fullName,
    required this.retakeScore,
    required this.qualityScore,
    required this.difficultyScore,
    required this.overallScore,
    required this.lastTimeTaught,
    required this.isPolarizing,
    required this.rmpTags,
  });

  @override
  Widget build(BuildContext context) {
    if (!isExpanded) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: const Color(0xFF0B0A14),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Row(
            children: [
              Container(
                width: 38,
                height: 38,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF2563EB)),
                ),
                child: Text(
                  initials,
                  style: const TextStyle(
                    color: Color(0xFF60A5FA),
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Text(
                  fullName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              Container(
                width: 44,
                height: 44,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF2563EB), width: 1.4),
                ),
                child: Text(
                  overallScore.toStringAsFixed(0),
                  style: const TextStyle(
                    color: Color(0xFF60A5FA),
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final archetype = (professor['archetype'] ?? 'The NPC').toString();

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF0B0A14),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // left side
              SizedBox(
                width: 150,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      archetype,
                      style: const TextStyle(
                        color: Color(0xFFB56CFF),
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Container(
                      width: 62,
                      height: 62,
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFF171624),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Image.asset(
                        archetypeImage,
                        fit: BoxFit.contain,
                      ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      archetypeDescription,
                      style: const TextStyle(
                        color: Color(0xFFCBC4D7),
                        fontSize: 14,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 10),
                    _InfoLine(label: 'Last Time Taught', value: lastTimeTaught),
                    const SizedBox(height: 6),
                    _InfoLine(
                      label: 'Controversial',
                      value: isPolarizing ? 'Yes' : 'No',
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 18),

              // right side
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            fullName,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                        ),
                        IconButton(
                          onPressed: onStarTap,
                          icon: Icon(
                            isStarred ? Icons.star : Icons.star_border,
                            color: const Color(0xFFB9B3C9),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    _ScoreBar(label: 'Retake Score', value: retakeScore),
                    const SizedBox(height: 12),
                    _ScoreBar(label: 'Quality Score', value: qualityScore),
                    const SizedBox(height: 12),
                    _ScoreBar(label: 'Difficulty Score', value: difficultyScore),
                    const SizedBox(height: 12),
                    _ScoreBar(label: 'Overall Score', value: overallScore),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 18),

          Align(
            alignment: Alignment.centerLeft,
            child: Wrap(
              spacing: 10,
              runSpacing: 10,
              children: rmpTags
                  .take(4)
                  .map(
                    (tag) => Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 9,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFF5A5A5A),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    tag,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              )
                  .toList(),
            ),
          ),

          const SizedBox(height: 14),

          Center(
            child: GestureDetector(
              onTap: onTap,
              child: const Text(
                '▲ Collapse',
                style: TextStyle(
                  color: Color(0xFF7F7895),
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ScoreBar extends StatelessWidget {
  final String label;
  final double value;

  const _ScoreBar({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final normalized = (value / 100).clamp(0.0, 1.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFFCBC4D7),
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(999),
                child: LinearProgressIndicator(
                  value: normalized,
                  minHeight: 6,
                  backgroundColor: const Color(0xFF3A3A46),
                  valueColor: const AlwaysStoppedAnimation<Color>(
                    Color(0xFF3B82F6),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            SizedBox(
              width: 42,
              child: Text(
                value.toStringAsFixed(0),
                textAlign: TextAlign.right,
                style: const TextStyle(
                  color: Color(0xFF60A5FA),
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _InfoLine extends StatelessWidget {
  final String label;
  final String value;

  const _InfoLine({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return RichText(
      text: TextSpan(
        children: [
          TextSpan(
            text: '$label: ',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 13,
              fontWeight: FontWeight.w700,
            ),
          ),
          TextSpan(
            text: value,
            style: const TextStyle(
              color: Color(0xFFCBC4D7),
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
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
          width: 140,
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
      width: 320,
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
                width: 36,
                height: 36,
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