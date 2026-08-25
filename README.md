# Production-Grade Enterprise AI Platform

A full-stack, production-ready Enterprise AI & Multi-Agent Engine built with **FastAPI**, **PostgreSQL 16 + pgvector**, **Redis**, **Ollama ($0 Local LLM)**, **Google Gemini SDK**, **FastEmbed**, and **Docker**.

---

## 🌟 Key Platform Capabilities

1. **$0 Free Local LLM Integration:** Local Ollama (`llama3.2`) as primary provider with zero API cost, auto-fallback to Gemini SDK.
2. **Hybrid RAG Search Engine:** Dense vector similarity search (FastEmbed cosine embeddings) combined with Sparse Lexical Keyword search (RRF & Cross-Encoder Reranking).
3. **Autonomous ReAct AI Agent:** ReAct reasoning loop with tool calling (`search_documents`, `get_employee_info`, `get_sales_report`, `create_support_ticket`).
4. **Natural Language Text-to-SQL Engine:** Direct natural language queries against relational database tables (`departments`, `employee_records`, `sales`) with strict SQL security validation blocking mutating statements (`DROP`, `DELETE`, `UPDATE`).
5. **Human-in-the-Loop (HITL) Safety Workflows:** Automated risk staging for high-impact agent tools requiring human manager approval (`GET /api/approvals/pending`, `POST /api/approvals/{task_id}/approve`) with complete audit trails.
6. **Stateful Multi-Turn Memory Manager:** Sliding message window with rolling auto-summarization for continuous context preservation across thousands of conversation turns.
7. **Business Intelligence (BI) & Analytics Engine:** Automated KPI extraction and multi-series chart data generation (`KPICard`, `ChartDataPoint`).
8. **Multi-Section Business Report Generator:** Multi-source context fusion (PDF RAG + SQL BI tables) synthesizing formal multi-section Markdown report artifacts saved on disk (`data/reports/`).
9. **RAG & LLM Evaluation Framework:** LLM-as-a-Judge benchmark suite evaluating the **RAG Triad** (Context Relevance, Faithfulness, Answer Relevance) exported to `evaluation/eval_report.json`.
10. **Observability, Tracing & Cost Telemetry:** Real-time request latency span tracking (`embedding_ms`, `retrieval_ms`, `llm_ms`), token consumption logging, and cost attribution dashboard (`GET /api/observability/metrics`).
11. **Security Guardrails & PII Redaction:** Direct prompt injection attack scanner blocking jailbreak attempts and automatically redacting PII (`SSN`, `Credit Card`, `Secrets`).
12. **Containerization & CI/CD:** Multi-stage production `Dockerfile`, `docker-compose.yml`, GitHub Actions workflow, and Single-Tenant Cloud Deployment guide.

---

## 🗺️ Complete API Endpoint Sitemap (18 Endpoints)

| Category | Method | Endpoint Path | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/health` | System health check & DB ping |
| **Auth** | `POST` | `/api/users` | User registration |
| **Auth** | `POST` | `/api/auth/login` | OAuth2 JWT token login |
| **Auth** | `GET` | `/api/auth/me` | Current authenticated user profile |
| **AI Chat** | `POST` | `/api/ai/chat` | Direct LLM chat with Redis caching |
| **Documents** | `POST` | `/api/documents/upload` | Ingest PDF/Text document into vector DB |
| **Documents** | `GET` | `/api/documents` | List user ingested documents |
| **RAG** | `POST` | `/api/search/hybrid` | Hybrid Vector + Lexical Search |
| **RAG** | `POST` | `/api/ai/rag/hybrid` | Hybrid RAG Q&A with citations |
| **AI Agent** | `POST` | `/api/ai/agent/chat` | Autonomous ReAct Agent with Tool Calling |
| **Text-to-SQL** | `POST` | `/api/ai/sql/query` | Natural Language to SQL Database Queries |
| **HITL** | `GET` | `/api/approvals/pending` | List pending high-risk approval tasks |
| **HITL** | `POST` | `/api/approvals/{task_id}/approve` | Approve staged action |
| **HITL** | `POST` | `/api/approvals/{task_id}/reject` | Reject staged action |
| **Memory** | `POST` | `/api/conversations/{id}/chat` | Multi-turn chat with rolling memory |
| **BI Analytics**| `POST` | `/api/ai/bi/analytics` | Database aggregations & KPI chart series |
| **Reports** | `POST` | `/api/ai/reports/generate` | Generate downloadable executive report .md |
| **Evaluation**| `POST` | `/api/ai/evaluation/run` | Run RAG Triad benchmark suite |
| **Observability**| `GET` | `/api/observability/metrics` | System telemetry, P90 latency & cost |
| **Security** | `POST` | `/api/ai/security/sanitize` | Prompt injection inspector & PII redactor |

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
docker-compose up db redis -d

# 3. Run FastAPI Production Server
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000

# 4. Run Pytest Integration Test Suite
PYTHONPATH=backend pytest backend/tests/
```
