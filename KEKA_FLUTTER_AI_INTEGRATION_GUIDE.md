# 📱 Keka Clone Flutter ERP — Master AI Integration Guide (All 15+ AI Features)

This master guide provides complete step-by-step instructions, Dart code snippets, and UI integration patterns for connecting your **Keka Clone Flutter ERP app** to all **15+ AI Features** on your **Enterprise AI Backend** running locally on your Mac (`http://localhost:8000`).

---

## 🏗️ Master Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────────┐
│                   Keka Clone Flutter ERP App                     │
│  (Recruiting, Approvals, Attendance ML, Voice, RAG, BI Reports)  │
└────────────────────────────────┬─────────────────────────────────┘
                                 │ HTTP REST (JWT Bearer Token)
┌────────────────────────────────▼─────────────────────────────────┐
│               FastAPI Enterprise AI Backend API                  │
│                     (http://localhost:8000)                      │
└───────────────┬────────────────────────────────┬─────────────────┘
                │                                │
┌───────────────▼──────────┐         ┌───────────▼──────────────┐
│ Local Ollama (llama3.2)  │         │ PostgreSQL + pgvector    │
│    (100% $0 API Cost)    │         │ (Users, Tasks, Audits)   │
└──────────────────────────┘         └──────────────────────────┘
```

---

## 🔑 Master Flutter API Service (`lib/services/ai_api_service.dart`)

Copy and paste this complete `AiApiService` class into your Flutter ERP project (`lib/services/ai_api_service.dart`).

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class AiApiService {
  // Use http://10.0.2.2:8000 for Android Emulator, http://127.0.0.1:8000 for iOS Simulator
  static const String baseUrl = 'http://127.0.0.1:8000/api';
  static String? _jwtToken;

  /// 1. AUTHENTICATION & JWT MANAGEMENT
  static Future<bool> login(String email, String password) async {
    final url = Uri.parse('$baseUrl/auth/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _jwtToken = data['access_token'];
      return true;
    }
    return false;
  }

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_jwtToken != null) 'Authorization': 'Bearer $_jwtToken',
      };

  // =========================================================================
  // SECTION A: VOICE & AUDIO AI ENGINES
  // =========================================================================

  /// Feature 1: Microsoft Edge Neural Voice TTS (100% Free, Male Voice Stream)
  static Future<List<int>> generateEdgeNeuralVoice(String text) async {
    final url = Uri.parse('$baseUrl/ai/tts/edge');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'text': text, 'voice': 'en-IN-PrabhatNeural'}),
    );
    return response.bodyBytes; // Audio MP3 bytes for AudioPlayer
  }

  /// Feature 2: ElevenLabs Premium Male Voice ("Adam")
  static Future<List<int>> generateElevenLabsVoice(String text) async {
    final url = Uri.parse('$baseUrl/ai/tts/elevenlabs');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'text': text}),
    );
    return response.bodyBytes;
  }

  /// Feature 3: Speech-to-Text Transcriber ("Mark" Voice Assistant)
  static Future<Map<String, dynamic>> transcribeAudio(File audioFile) async {
    final url = Uri.parse('$baseUrl/ai/stt/transcribe');
    final request = http.MultipartRequest('POST', url);
    if (_jwtToken != null) request.headers['Authorization'] = 'Bearer $_jwtToken';
    request.fields['language'] = 'en-IN';
    request.files.add(await http.MultipartFile.fromPath('file', audioFile.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return jsonDecode(response.body);
  }

  // =========================================================================
  // SECTION B: AUTONOMOUS AGENTS & COPILOTS
  // =========================================================================

  /// Feature 4: Autonomous Multi-Tool ERP AI Agent
  static Future<Map<String, dynamic>> runAutonomousAgent(String prompt) async {
    final url = Uri.parse('$baseUrl/ai/agent/chat');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'prompt': prompt}),
    );
    return jsonDecode(response.body);
  }

  /// Feature 5: Natural Language SQL Analytics Agent
  static Future<Map<String, dynamic>> querySqlAgent(String query) async {
    final url = Uri.parse('$baseUrl/ai/sql/query');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'query': query}),
    );
    return jsonDecode(response.body);
  }

  /// Feature 6: Manager Approval Copilot Summary
  static Future<Map<String, dynamic>> getApprovalCopilotSummary(int taskId) async {
    final url = Uri.parse('$baseUrl/approvals/$taskId/copilot-summary');
    final response = await http.get(url, headers: _headers);
    return jsonDecode(response.body);
  }

  /// Feature 7: Human-in-the-Loop (HITL) Task Approval / Rejection
  static Future<Map<String, dynamic>> reviewApprovalTask(int taskId, bool approve, String reason) async {
    final action = approve ? 'approve' : 'reject';
    final url = Uri.parse('$baseUrl/approvals/$taskId/$action');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'reason': reason}),
    );
    return jsonDecode(response.body);
  }

  // =========================================================================
  // SECTION C: HR & RECRUITMENT AI SUITE
  // =========================================================================

  /// Feature 8: Candidate Resume Parsing & AI Scoring
  static Future<Map<String, dynamic>> scoreCandidateResume(File resumeFile, String jobDescription) async {
    final url = Uri.parse('$baseUrl/recruitment/resumes/score');
    final request = http.MultipartRequest('POST', url);
    if (_jwtToken != null) request.headers['Authorization'] = 'Bearer $_jwtToken';
    request.fields['job_description'] = jobDescription;
    request.files.add(await http.MultipartFile.fromPath('file', resumeFile.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return jsonDecode(response.body);
  }

  /// Feature 9: Predictive Attendance Anomaly & Burnout ML
  static Future<Map<String, dynamic>> getAttendanceAnomalies() async {
    final url = Uri.parse('$baseUrl/analytics/attendance/anomalies');
    final response = await http.get(url, headers: _headers);
    return jsonDecode(response.body);
  }

  /// Feature 10: Smart Shift & Roster Optimization AI
  static Future<Map<String, dynamic>> optimizeRoster(Map<String, dynamic> rosterPayload) async {
    final url = Uri.parse('$baseUrl/ai/roster/optimize');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode(rosterPayload),
    );
    return jsonDecode(response.body);
  }

  // =========================================================================
  // SECTION D: ENTERPRISE RAG & BI REPORTING
  // =========================================================================

  /// Feature 11: Enterprise Hybrid RAG Policy Search
  static Future<Map<String, dynamic>> queryPolicyRAG(String query) async {
    final url = Uri.parse('$baseUrl/ai/rag/hybrid');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'query': query, 'top_k': 3}),
    );
    return jsonDecode(response.body);
  }

  /// Feature 12: Automated Executive BI Report Generator
  static Future<Map<String, dynamic>> generateBiReport(String reportType) async {
    final url = Uri.parse('$baseUrl/reports/executive');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'report_type': reportType}),
    );
    return jsonDecode(response.body);
  }

  /// Feature 13: Document PDF Ingestion & Ingesting
  static Future<Map<String, dynamic>> uploadDocument(File pdfFile, String category) async {
    final url = Uri.parse('$baseUrl/documents/upload');
    final request = http.MultipartRequest('POST', url);
    if (_jwtToken != null) request.headers['Authorization'] = 'Bearer $_jwtToken';
    request.fields['category'] = category;
    request.files.add(await http.MultipartFile.fromPath('file', pdfFile.path));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return jsonDecode(response.body);
  }

  // =========================================================================
  // SECTION E: SECURITY & OBSERVABILITY METRICS
  // =========================================================================

  /// Feature 14: Enterprise Security & Guardrails Audit
  static Future<Map<String, dynamic>> runSecurityAudit(String prompt) async {
    final url = Uri.parse('$baseUrl/security/audit');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'prompt': prompt}),
    );
    return jsonDecode(response.body);
  }

  /// Feature 15: AI System Telemetry & Cost Metrics
  static Future<Map<String, dynamic>> getTelemetryMetrics() async {
    final url = Uri.parse('$baseUrl/observability/metrics');
    final response = await http.get(url, headers: _headers);
    return jsonDecode(response.body);
  }
}
```

---

## 🎨 Master Flutter UI Component Integration Matrix

### 1. Voice Assistant Speech-to-Text & Male Neural TTS ("Mark")
* **Flutter Widget:** Floating Action Button (Mic) + `audioplayers` package.
* **Code:**
  ```dart
  void speakResponse(String text) async {
    List<int> mp3Bytes = await AiApiService.generateEdgeNeuralVoice(text);
    // Play mp3Bytes using AudioPlayer().play(BytesSource(mp3Bytes));
  }
  ```

---

### 2. Natural Language SQL Analytics Bar (`sql_analytics_screen.dart`)
* **Flutter Widget:** Search Bar accepting natural questions like `"Show total sales by region"`.
* **Code:**
  ```dart
  void queryDatabase(String queryText) async {
    final result = await AiApiService.querySqlAgent(queryText);
    String generatedSql = result['sql_query'];
    List rows = result['results'];
    // Render DataTable in Flutter UI
  }
  ```

---

### 3. Manager Approval Copilot Card (`manager_approvals_screen.dart`)
* **Flutter Widget:** Approval Task Card showing AI recommendation badge (`RECOMMEND_APPROVAL`, `REQUIRES_REVIEW`) and conflict analysis.

---

### 4. Candidate Resume Scoring Card (`recruitment_screen.dart`)
* **Flutter Widget:** Circular fit score gauge (0-100%) and skill chips.

---

### 5. Attendance Anomaly & Burnout Heatmap (`attendance_dashboard.dart`)
* **Flutter Widget:** Employee list showing burnout probability percentage bars.

---

### 6. Executive BI Report Generator (`bi_reports_screen.dart`)
* **Flutter Widget:** Export Button triggering automated markdown executive report generation.

---

## 🌐 Environment & IP Matrix

| Device Type | API Base URL |
| :--- | :--- |
| **iOS Simulator (Mac)** | `http://127.0.0.1:8000/api` |
| **Android Emulator** | `http://10.0.2.2:8000/api` |
| **Physical Mac / iPhone / Android** | `http://<YOUR_MAC_IP_ADDRESS>:8000/api` |
