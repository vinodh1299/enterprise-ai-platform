# Production-Grade Enterprise AI Platform (Keka ERP AI Backend)

![Enterprise AI CI/CD Pipeline](https://github.com/vinodh1299/enterprise-ai-platform/actions/workflows/deploy.yml/badge.svg)

A full-stack, production-ready Enterprise AI & Multi-Agent Engine built with **FastAPI**, **PostgreSQL 16 + pgvector**, **Redis**, **Ollama ($0 Local LLM - `llama3.2`)**, **Google Gemini SDK**, **FastEmbed**, and **Docker**.

---

## 🌟 Key Platform Capabilities & ERP AI Roadmap

1. **$0 Free Local LLM Integration:** Local Ollama (`llama3.2`) as primary provider with zero API cost, auto-fallback to Gemini SDK.
2. **Automated Candidate Resume Parser & AI Scoring:** Extracts PDF/DOCX/TXT candidate resumes and scores fit (0-100%) against job descriptions with skill extractions and red flag warnings (`POST /api/recruitment/resumes/score`).
3. **Manager Approval Copilot AI:** Evaluates pending staged HITL tasks, team calendar overlaps, and generates executive manager recommendations (`GET /api/approvals/{task_id}/copilot-summary`).
4. **Predictive Attendance Anomaly & Burnout ML:** Analyzes clock-in/out patterns, late arrivals, and predicts employee burnout risk scores (0-100%) (`GET /api/analytics/attendance/anomalies`).
5. **Speech-to-Text (STT) Audio Microservice:** Transcribes audio files (`.wav`, `.mp3`, `.m4a`, `.ogg`) with Indian-English accent processing and intent extraction (`POST /api/ai/stt/transcribe`).
6. **Smart Shift & Roster Optimization AI:** Constraint-satisfaction AI shift scheduler balancing employee availability, requested leave dates, skill requirements, and rest gaps (`POST /api/ai/roster/optimize`).
7. **Neural & Ultra-Realistic Male Voice AI:** Microsoft Edge Neural Male Voice (`msedge-tts`) and ElevenLabs Male Voice ("Adam") for speech synthesis.
8. **Hybrid RAG Search Engine:** Dense vector similarity search (FastEmbed cosine embeddings) combined with Sparse Lexical Keyword search (RRF & Cross-Encoder Reranking).
9. **Autonomous ReAct AI Agent:** ReAct reasoning loop with tool calling (`search_documents`, `get_employee_info`, `get_sales_report`, `create_support_ticket`).
10. **Natural Language Text-to-SQL Engine:** Direct natural language queries against relational database tables (`departments`, `employee_records`, `sales`) with strict SQL security validation blocking mutating statements (`DROP`, `DELETE`, `UPDATE`).
11. **Human-in-the-Loop (HITL) Safety Workflows:** Automated risk staging for high-impact agent tools requiring human manager approval (`GET /api/approvals/pending`, `POST /api/approvals/{task_id}/approve`) with complete audit trails.
12. **Multi-Section Business Report Generator:** Multi-source context fusion (PDF RAG + SQL BI tables) synthesizing formal multi-section Markdown report artifacts saved on disk (`data/reports/`).
13. **Observability, Tracing & Cost Telemetry:** Real-time request latency span tracking (`embedding_ms`, `retrieval_ms`, `llm_ms`), token consumption logging, and cost attribution dashboard (`GET /api/observability/metrics`).

---

## 🗺️ Master API Endpoint Sitemap (25 Endpoints)

| Category | Method | Endpoint Path | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/health` | System health check & DB ping |
| **Auth** | `POST` | `/api/users` | User registration |
| **Auth** | `POST` | `/api/auth/login` | OAuth2 / HTTPBearer JWT token login |
| **Auth** | `GET` | `/api/users/me` | Current authenticated user profile |
| **Recruitment AI** | `POST` | `/api/recruitment/resumes/score` | Candidate Resume Parser & AI Scoring (PDF/DOCX) |
| **Approval Copilot**| `GET` | `/api/approvals/{task_id}/copilot-summary` | AI Manager Approval Copilot Summary & Conflict Check |
| **Attendance ML** | `GET` | `/api/analytics/attendance/anomalies` | Predictive Attendance Anomaly & Burnout ML |
| **Voice STT** | `POST` | `/api/ai/stt/transcribe` | Speech-to-Text Audio Transcriber ("Mark" Assistant) |
| **Roster AI** | `POST` | `/api/ai/roster/optimize` | Smart Shift & Roster Optimization AI Scheduler |
| **Voice TTS** | `POST` | `/api/ai/tts/edge` | Microsoft Edge Neural Male Voice Stream (100% Free) |
| **Voice TTS** | `POST` | `/api/ai/tts/elevenlabs` | ElevenLabs Ultra-Realistic Male Voice ("Adam") |
| **AI Chat** | `POST` | `/api/ai/chat` | Direct LLM chat with Redis caching |
| **Documents** | `POST` | `/api/documents/upload` | Ingest PDF/Text document into vector DB |
| **Documents** | `GET` | `/api/documents` | List user ingested documents |
| **RAG** | `POST` | `/api/ai/rag/hybrid` | Hybrid RAG Q&A with citations |
| **AI Agent** | `POST` | `/api/ai/agent/chat` | Autonomous ReAct Agent with Tool Calling |
| **Text-to-SQL** | `POST` | `/api/ai/sql/query` | Natural Language to SQL Database Queries |
| **HITL** | `GET` | `/api/approvals/pending` | List pending high-risk approval tasks |
| **HITL** | `POST` | `/api/approvals/{task_id}/approve` | Approve staged action |
| **HITL** | `POST` | `/api/approvals/{task_id}/reject` | Reject staged action |
| **HITL Audit** | `GET` | `/api/audit-logs` | Fetch enterprise audit trail logs |
| **BI Analytics**| `POST` | `/api/ai/bi/analytics` | Database aggregations & KPI chart series |
| **Reports** | `POST` | `/api/reports/executive` | Generate downloadable executive report .md |
| **Observability**| `GET` | `/api/observability/metrics` | System telemetry, P90 latency & cost |
| **Security** | `POST` | `/api/security/audit` | Prompt injection inspector & PII redactor |

---

## 📱 Flutter ERP Integration Guide

Complete Dart code service class and UI integration guide for connecting Keka Clone Flutter ERP app:
👉 **[`KEKA_FLUTTER_AI_INTEGRATION_GUIDE.md`](file:///Users/acamedia/VINODH/AI%20ENGINEERING/KEKA_FLUTTER_AI_INTEGRATION_GUIDE.md)**

---

## 🛠️ Technology Stack

* **Backend Framework:** FastAPI (Python 3.9+)
* **Database & Vectors:** PostgreSQL 16 + `pgvector` extension
* **ORM & Migrations:** SQLAlchemy (AsyncIO) + Alembic
* **Primary LLM Engine:** Ollama (`llama3.2` locally at `http://localhost:11434`) + Google Gemini SDK fallback
* **Embeddings:** FastEmbed (`BAAI/bge-small-en-v1.5` 384-dim)
* **Caching & Sessions:** Redis 7
* **Containerization:** Docker & Docker Compose
* **CI/CD:** GitHub Actions
* **Testing:** Pytest (AsyncIO + HTTPX)

---

## ⚡ Quickstart Development Instructions

```bash
# 1. Activate Python Virtual Environment
source .venv/bin/activate

# 2. Run Database Migration & PostgreSQL Container
docker compose up db redis -d

# 3. Run FastAPI Production Server
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000

# 4. Run Pytest Integration Test Suite (20 Integration Tests)
PYTHONPATH=backend pytest backend/tests/
```
