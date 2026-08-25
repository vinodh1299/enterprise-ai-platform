# Architecture Decision Record (ADR) 0001: Initial Tech Stack & Project Architecture

## Context & Problem Statement
We need to establish a foundational architecture for an Enterprise AI Operations Platform that supports document RAG, AI Tool calling, Text-to-SQL capabilities, evaluation, and enterprise security, while maintaining extreme code clarity for learning purposes.

## Decision
We will build a **Modular Monolith** backend using **FastAPI (Python)** and **PostgreSQL + pgvector** as our primary relational and vector data store.

### Key Technology Choices:
1. **Backend Framework:** FastAPI (Python 3.11+)
   * *Reason:* Async I/O support, native Pydantic validation, automatic OpenAPI specification generation, and top-tier Python AI ecosystem integration.
2. **Database:** PostgreSQL with `pgvector` extension
   * *Reason:* Avoids unnecessary operational complexity early on. PostgreSQL handles structured user/rbac/audit data AND vector embeddings in a single ACID-compliant database.
3. **Database ORM & Migrations:** SQLAlchemy 2.0 (Async) + Alembic
   * *Reason:* Standard enterprise-grade Python ORM providing type-safe async queries and version-controlled database schema migrations.
4. **Environment Isolation:** Python Virtual Environment (`.venv`) + `.env` secrets separation.

## Status
Accepted

## Consequences & Trade-offs
* **Positive:** Reduced infrastructure overhead, faster iteration, single database technology to maintain initially.
* **Negative:** PostgreSQL with `pgvector` will eventually require tuning or migration to a specialized vector database (e.g., Qdrant) if vector scale exceeds tens of millions of high-dimensional embeddings.
* **Mitigation:** Database operations will be abstracted behind Repository interfaces (`backend/app/repositories/`) to allow swapping vector backends without rewriting core AI business logic.
