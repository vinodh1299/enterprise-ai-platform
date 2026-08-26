# 📱 Keka Clone Flutter ERP — Complete AI Integration Guide

This guide provides step-by-step instructions, Dart code snippets, and UI integration patterns for connecting your **Keka Clone Flutter ERP app** to the **Enterprise AI Backend** running locally on your Mac (`http://localhost:8000`).

---

## 🏗️ Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│              Keka Clone Flutter ERP App                │
│ (Recruiting / Manager Approvals / HR Analytics / Voice)│
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP REST (JWT Bearer Token)
┌──────────────────────────▼─────────────────────────────┐
│             FastAPI Enterprise AI Backend              │
│                 (http://localhost:8000)                │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
┌──────────────▼──────────┐    ┌──────────▼──────────────┐
│ Local Ollama (llama3.2) │    │ PostgreSQL + pgvector   │
│   (100% $0 API Cost)    │    │ (Users, Tasks, Audits)  │
└─────────────────────────┘    └─────────────────────────┘
```

---

## 🔑 Step 1: Central Flutter API Service (`lib/services/ai_api_service.dart`)

Create this file in your Flutter project to handle authentication and communication with all AI endpoints.

```dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class AiApiService {
  // Use http://10.0.2.2:8000 for Android Emulator, http://127.0.0.1:8000 for iOS Simulator
  static const String baseUrl = 'http://127.0.0.1:8000/api';
  static String? _jwtToken;

  /// 1. Authenticate user and store JWT token
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

  /// 2. Feature 1: Candidate Resume Parsing & AI Scoring
  static Future<Map<String, dynamic>> scoreCandidateResume(
      File resumeFile, String jobDescription) async {
    final url = Uri.parse('$baseUrl/recruitment/resumes/score');
    final request = http.MultipartRequest('POST', url);
    if (_jwtToken != null) {
      request.headers['Authorization'] = 'Bearer $_jwtToken';
    }

    request.fields['job_description'] = jobDescription;
    request.files.add(
      await http.MultipartFile.fromPath('file', resumeFile.path),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    return jsonDecode(response.body);
  }

  /// 3. Feature 2: Manager Approval Copilot Summary
  static Future<Map<String, dynamic>> getApprovalCopilotSummary(int taskId) async {
    final url = Uri.parse('$baseUrl/approvals/$taskId/copilot-summary');
    final response = await http.get(url, headers: _headers);
    return jsonDecode(response.body);
  }

  /// 4. Feature 3: Predictive Attendance Anomaly & Burnout Risk ML
  static Future<Map<String, dynamic>> getAttendanceAnomalies() async {
    final url = Uri.parse('$baseUrl/analytics/attendance/anomalies');
    final response = await http.get(url, headers: _headers);
    return jsonDecode(response.body);
  }

  /// 5. Feature 4: Speech-to-Text (STT) Audio Transcription ("Mark")
  static Future<Map<String, dynamic>> transcribeAudio(File audioFile) async {
    final url = Uri.parse('$baseUrl/ai/stt/transcribe');
    final request = http.MultipartRequest('POST', url);
    if (_jwtToken != null) {
      request.headers['Authorization'] = 'Bearer $_jwtToken';
    }

    request.fields['language'] = 'en-IN';
    request.files.add(
      await http.MultipartFile.fromPath('file', audioFile.path),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    return jsonDecode(response.body);
  }

  /// 6. Feature 5: Smart Shift & Roster Optimization AI
  static Future<Map<String, dynamic>> optimizeRoster(Map<String, dynamic> rosterPayload) async {
    final url = Uri.parse('$baseUrl/ai/roster/optimize');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode(rosterPayload),
    );
    return jsonDecode(response.body);
  }

  /// 7. Feature 6: HR Policy Hybrid RAG Search
  static Future<Map<String, dynamic>> queryPolicyRAG(String query) async {
    final url = Uri.parse('$baseUrl/ai/rag/hybrid');
    final response = await http.post(
      url,
      headers: _headers,
      body: jsonEncode({'query': query, 'top_k': 3}),
    );
    return jsonDecode(response.body);
  }
}
```

---

## 🎨 Step 2: UI Feature Integration Guide

### 1. Candidate Resume Parsing & AI Scoring Screen (`recruitment_screen.dart`)

**Where to use:** Candidate Application Detail screen in your HR module.

```dart
void uploadAndScoreResume(File file) async {
  final result = await AiApiService.scoreCandidateResume(
    file, 
    "Senior Flutter Engineer: 3+ years experience with Dart, REST APIs, and State Management."
  );
  
  // Display Candidate Score Card in Flutter UI
  setState(() {
    int score = result['overall_score']; // e.g. 88
    String summary = result['summary'];
    List skills = result['key_skills'];
    List redFlags = result['red_flags'];
  });
}
```

**UI Pattern:** Display a Circular Progress Bar for `overall_score` (Green for $\ge 75$, Yellow for $50-74$, Red for $<50$), followed by chips for `key_skills` and warning banners for `red_flags`.

---

### 2. Manager Approval Copilot Card (`manager_approvals_screen.dart`)

**Where to use:** When a Manager taps on a pending Leave/Regularization request.

```dart
Widget buildCopilotCard(int taskId) {
  return FutureBuilder<Map<String, dynamic>>(
    future: AiApiService.getApprovalCopilotSummary(taskId),
    builder: (context, snapshot) {
      if (!snapshot.hasData) return CircularProgressIndicator();
      
      final data = snapshot.data!;
      final rec = data['recommendation']; // RECOMMEND_APPROVAL / REQUIRES_REVIEW
      final summary = data['executive_summary'];
      final conflicts = data['conflict_risks'] as List;

      return Card(
        color: rec == 'RECOMMEND_APPROVAL' ? Colors.green.shade50 : Colors.amber.shade50,
        child: ListTile(
          leading: Icon(
            rec == 'RECOMMEND_APPROVAL' ? Icons.check_circle : Icons.warning,
            color: rec == 'RECOMMEND_APPROVAL' ? Colors.green : Colors.amber.shade800,
          ),
          title: Text("AI Recommendation: $rec"),
          subtitle: Text(summary),
        ),
      );
    },
  );
}
```

---

### 3. Predictive Attendance & Burnout Analytics Dashboard (`attendance_dashboard.dart`)

**Where to use:** HR Analytics / Team Attendance overview tab.

```dart
void loadAttendanceAnalytics() async {
  final data = await AiApiService.getAttendanceAnomalies();
  List burnoutList = data['burnout_risk_list'];
  
  for (var emp in burnoutList) {
    print("${emp['employee_name']}: Risk ${emp['burnout_risk_score']}% (${emp['risk_level']})");
  }
}
```

**UI Pattern:** Render a heatmap list of employees with progress indicators showing `burnout_risk_score` to proactively manage staff workload.

---

### 4. Voice Assistant "Mark" STT Integration (`voice_assistant_widget.dart`)

**Where to use:** Floating Action Button (FAB) microphone icon on your home screen.

```dart
void onRecordComplete(File audioFile) async {
  final sttResult = await AiApiService.transcribeAudio(audioFile);
  String text = sttResult['transcript_text'];
  List intents = sttResult['extracted_intents'];

  // Route to action based on intent
  if (intents.contains("LEAVE_APPLICATION")) {
    Navigator.pushNamed(context, '/apply-leave', arguments: text);
  }
}
```

---

### 5. Smart Shift Roster Optimizer (`roster_screen.dart`)

**Where to use:** Shift Scheduler / Roster Management tab.

```dart
void generateWeeklyRoster() async {
  final response = await AiApiService.optimizeRoster({
    "department": "Operations",
    "target_week_start": "2026-08-31",
    "shift_requirements": [
      {
        "shift_name": "Morning Shift",
        "start_time": "09:00",
        "end_time": "17:00",
        "min_staff_required": 3,
        "required_skills": ["Customer Support"]
      }
    ],
    "available_employees": [
      {
        "employee_id": 1,
        "employee_name": "John Doe",
        "department": "Operations",
        "skills": ["Customer Support"],
        "leave_dates": []
      }
    ]
  });

  print("Assigned ${response['total_shifts_assigned']} shifts cleanly!");
}
```

---

### 6. HR Policy RAG Chat Widget (`policy_chat_widget.dart`)

**Where to use:** Employee Self-Service (ESS) Helpdesk Chatbot.

```dart
void askPolicyBot(String userQuestion) async {
  final ragResult = await AiApiService.queryPolicyRAG(userQuestion);
  String botResponse = ragResult['response'];
  List sources = ragResult['source_documents'];
  
  // Render chat bubble with botResponse & citations
}
```

---

## ⚡ Environment Matrix for Device Testing

| Device Type | API Base URL |
| :--- | :--- |
| **iOS Simulator (Mac)** | `http://127.0.0.1:8000/api` |
| **Android Emulator** | `http://10.0.2.2:8000/api` |
| **Physical iPhone / Android** | `http://<YOUR_MAC_IP_ADDRESS>:8000/api` |

*(To find your Mac IP address, run `ipconfig getifaddr en0` in your terminal).*

---

## 🏁 Summary Checklist

- [x] Backend running on `http://localhost:8000`
- [x] Docker containers running (`docker compose up db redis -d`)
- [x] Add `AiApiService` to your Flutter project
- [x] Log in with `myadmin@enterprise.com` / `PassWord123!` to obtain JWT Token
- [x] Connect screens: Resume Scoring, Manager Copilot, Attendance ML, Voice Assistant, Roster AI, Policy RAG!
